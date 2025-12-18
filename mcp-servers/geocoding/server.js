import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3004;

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org';
const PHOTON_URL = 'https://photon.komoot.io';

app.use(cors());
app.use(express.json());

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'mcp-geocoding-server',
    apis: ['Nominatim', 'Photon'],
    note: 'No API keys required!'
  });
});

app.post('/geocode', async (req, res) => {
  try {
    const { address } = req.body;

    if (!address) {
      return res.status(400).json({
        error: 'Address is required',
        message: 'Please provide an address to geocode'
      });
    }

    await delay(1000);

    const response = await axios.get(`${NOMINATIM_URL}/search`, {
      params: {
        q: address,
        format: 'json',
        addressdetails: 1,
        limit: 1
      },
      headers: {
        'User-Agent': 'EventPlannerAgent/1.0'
      }
    });

    if (response.data.length === 0) {
      return res.status(404).json({
        error: 'Location not found',
        message: `Could not geocode address: ${address}`
      });
    }

    const result = response.data[0];
    res.json({
      success: true,
      source: 'nominatim',
      address: result.display_name,
      latitude: parseFloat(result.lat),
      longitude: parseFloat(result.lon),
      place_id: result.place_id,
      osm_type: result.osm_type,
      osm_id: result.osm_id,
      boundingbox: result.boundingbox
    });

  } catch (error) {
    console.error('Nominatim geocoding error:', error.message);
    res.status(500).json({
      error: 'Geocoding failed',
      message: error.message
    });
  }
});

app.post('/reverse-geocode', async (req, res) => {
  try {
    const { latitude, longitude } = req.body;

    if (!latitude || !longitude) {
      return res.status(400).json({
        error: 'Latitude and longitude are required'
      });
    }

    await delay(1000);

    const response = await axios.get(`${NOMINATIM_URL}/reverse`, {
      params: {
        lat: latitude,
        lon: longitude,
        format: 'json',
        addressdetails: 1
      },
      headers: {
        'User-Agent': 'EventPlannerAgent/1.0'
      }
    });

    res.json({
      success: true,
      source: 'nominatim',
      address: response.data.display_name,
      place_id: response.data.place_id,
      osm_type: response.data.osm_type,
      osm_id: response.data.osm_id,
      address_details: response.data.address
    });

  } catch (error) {
    console.error('Nominatim reverse geocoding error:', error.message);
    res.status(500).json({
      error: 'Reverse geocoding failed',
      message: error.message
    });
  }
});

app.post('/places/search', async (req, res) => {
  try {
    const { query, latitude, longitude, limit = 10 } = req.body;

    if (!query) {
      return res.status(400).json({
        error: 'Query is required'
      });
    }

    const params = {
      q: query,
      limit: limit
    };

    if (latitude && longitude) {
      params.lat = latitude;
      params.lon = longitude;
    }

    const response = await axios.get(`${PHOTON_URL}/api`, {
      params: params
    });

    const places = response.data.features.map(feature => {
      const props = feature.properties;
      const coords = feature.geometry.coordinates;

      return {
        place_id: `photon_${props.osm_id}`,
        external_id: `osm_${props.osm_id}`,
        external_source: 'photon',
        name: props.name || 'Unnamed',
        address: formatPhotonAddress(props),
        latitude: coords[1],
        longitude: coords[0],
        osm_type: props.osm_type,
        osm_id: props.osm_id,
        type: props.type,
        city: props.city,
        state: props.state,
        country: props.country,
        postcode: props.postcode
      };
    });

    res.json({
      success: true,
      source: 'photon',
      query: query,
      count: places.length,
      places: places
    });

  } catch (error) {
    console.error('Photon search error:', error.message);
    res.status(500).json({
      error: 'Place search failed',
      message: error.message
    });
  }
});

app.post('/places/nearby', async (req, res) => {
  try {
    const { latitude, longitude, radius_km = 5, type, limit = 20 } = req.body;

    if (!latitude || !longitude) {
      return res.status(400).json({
        error: 'Latitude and longitude are required'
      });
    }

    const params = {
      lat: latitude,
      lon: longitude,
      limit: limit
    };

    if (type) {
      params.osm_tag = type;
    }

    const response = await axios.get(`${PHOTON_URL}/api`, {
      params: params
    });

    const places = response.data.features
      .map(feature => {
        const props = feature.properties;
        const coords = feature.geometry.coordinates;
        const distance = calculateDistance(latitude, longitude, coords[1], coords[0]);

        return {
          place_id: `photon_${props.osm_id}`,
          external_id: `osm_${props.osm_id}`,
          external_source: 'photon',
          name: props.name || 'Unnamed',
          address: formatPhotonAddress(props),
          latitude: coords[1],
          longitude: coords[0],
          distance_km: distance,
          osm_type: props.osm_type,
          osm_id: props.osm_id,
          type: props.type,
          city: props.city,
          state: props.state,
          country: props.country
        };
      })
      .filter(place => place.distance_km <= radius_km)
      .sort((a, b) => a.distance_km - b.distance_km);

    res.json({
      success: true,
      source: 'photon',
      center: { latitude, longitude },
      radius_km: radius_km,
      count: places.length,
      places: places
    });

  } catch (error) {
    console.error('Photon nearby search error:', error.message);
    res.status(500).json({
      error: 'Nearby search failed',
      message: error.message
    });
  }
});

app.get('/places/details/:place_id', async (req, res) => {
  try {
    const { place_id } = req.params;

    const osmId = place_id.replace('photon_', '').replace('osm_', '');

    await delay(1000);

    const response = await axios.get(`${NOMINATIM_URL}/lookup`, {
      params: {
        osm_ids: `N${osmId}`,
        format: 'json',
        addressdetails: 1,
        extratags: 1
      },
      headers: {
        'User-Agent': 'EventPlannerAgent/1.0'
      }
    });

    if (response.data.length === 0) {
      return res.status(404).json({
        error: 'Place not found'
      });
    }

    const place = response.data[0];
    res.json({
      success: true,
      source: 'nominatim',
      place_id: place.place_id,
      osm_type: place.osm_type,
      osm_id: place.osm_id,
      name: place.display_name,
      address: place.address,
      latitude: parseFloat(place.lat),
      longitude: parseFloat(place.lon),
      extratags: place.extratags,
      boundingbox: place.boundingbox
    });

  } catch (error) {
    console.error('Nominatim place details error:', error.message);
    res.status(500).json({
      error: 'Failed to get place details',
      message: error.message
    });
  }
});

function formatPhotonAddress(props) {
  const parts = [];
  if (props.housenumber) parts.push(props.housenumber);
  if (props.street) parts.push(props.street);
  if (props.city) parts.push(props.city);
  if (props.state) parts.push(props.state);
  if (props.postcode) parts.push(props.postcode);
  if (props.country) parts.push(props.country);
  return parts.join(', ') || 'Address not available';
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

app.listen(PORT, () => {
  console.log(`🌍 MCP Geocoding Server running on port ${PORT}`);
  console.log(`✅ Nominatim - No API key needed!`);
  console.log(`✅ Photon - No API key needed!`);
  console.log(`Using Nominatim: ${NOMINATIM_URL}`);
  console.log(`Using Photon: ${PHOTON_URL}`);
});
