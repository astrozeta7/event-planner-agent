import express from 'express';
import { Client } from '@googlemaps/google-maps-services-js';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3004;
const client = new Client({});

app.use(cors());
app.use(express.json());

const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY;

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'mcp-google-maps-server',
    apis: {
      google_maps: GOOGLE_MAPS_API_KEY ? 'configured' : 'missing'
    }
  });
});

app.post('/places/search', async (req, res) => {
  try {
    const { query, location, radius = 5000, type } = req.body;

    if (!GOOGLE_MAPS_API_KEY) {
      return res.status(500).json({ 
        error: 'Google Maps API key not configured',
        message: 'Please set GOOGLE_MAPS_API_KEY in environment variables'
      });
    }

    const response = await client.textSearch({
      params: {
        query: query,
        location: location,
        radius: radius,
        type: type,
        key: GOOGLE_MAPS_API_KEY
      }
    });

    const places = response.data.results.map(place => ({
      place_id: place.place_id,
      name: place.name,
      address: place.formatted_address,
      location: place.geometry.location,
      rating: place.rating,
      user_ratings_total: place.user_ratings_total,
      price_level: place.price_level,
      types: place.types,
      business_status: place.business_status,
      photos: place.photos?.map(photo => ({
        photo_reference: photo.photo_reference,
        width: photo.width,
        height: photo.height
      })),
      opening_hours: place.opening_hours
    }));

    res.json({
      success: true,
      count: places.length,
      data: places,
      metadata: {
        query: query,
        location: location,
        source: 'google_maps_places_api'
      }
    });

  } catch (error) {
    console.error('Google Maps API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to search places',
      message: error.response?.data?.error_message || error.message
    });
  }
});

app.post('/places/nearby', async (req, res) => {
  try {
    const { location, radius = 5000, type, keyword } = req.body;

    if (!GOOGLE_MAPS_API_KEY) {
      return res.status(500).json({ 
        error: 'Google Maps API key not configured'
      });
    }

    const response = await client.placesNearby({
      params: {
        location: location,
        radius: radius,
        type: type,
        keyword: keyword,
        key: GOOGLE_MAPS_API_KEY
      }
    });

    const places = response.data.results.map(place => ({
      place_id: place.place_id,
      name: place.name,
      vicinity: place.vicinity,
      location: place.geometry.location,
      rating: place.rating,
      user_ratings_total: place.user_ratings_total,
      price_level: place.price_level,
      types: place.types,
      business_status: place.business_status
    }));

    res.json({
      success: true,
      count: places.length,
      data: places
    });

  } catch (error) {
    console.error('Google Maps API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to search nearby places',
      message: error.response?.data?.error_message || error.message
    });
  }
});

app.post('/places/details/:place_id', async (req, res) => {
  try {
    const { place_id } = req.params;

    if (!GOOGLE_MAPS_API_KEY) {
      return res.status(500).json({ 
        error: 'Google Maps API key not configured'
      });
    }

    const response = await client.placeDetails({
      params: {
        place_id: place_id,
        fields: [
          'name',
          'formatted_address',
          'formatted_phone_number',
          'website',
          'rating',
          'user_ratings_total',
          'price_level',
          'opening_hours',
          'photos',
          'reviews',
          'geometry',
          'types',
          'business_status'
        ],
        key: GOOGLE_MAPS_API_KEY
      }
    });

    const place = response.data.result;

    res.json({
      success: true,
      data: {
        place_id: place.place_id,
        name: place.name,
        address: place.formatted_address,
        phone: place.formatted_phone_number,
        website: place.website,
        location: place.geometry?.location,
        rating: place.rating,
        user_ratings_total: place.user_ratings_total,
        price_level: place.price_level,
        opening_hours: place.opening_hours,
        reviews: place.reviews?.map(review => ({
          author_name: review.author_name,
          rating: review.rating,
          text: review.text,
          time: review.time,
          relative_time_description: review.relative_time_description
        })),
        photos: place.photos?.map(photo => ({
          photo_reference: photo.photo_reference,
          width: photo.width,
          height: photo.height
        })),
        types: place.types,
        business_status: place.business_status
      }
    });

  } catch (error) {
    console.error('Google Maps API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to fetch place details',
      message: error.response?.data?.error_message || error.message
    });
  }
});

app.post('/places/photo', async (req, res) => {
  try {
    const { photo_reference, maxwidth = 400 } = req.body;

    if (!GOOGLE_MAPS_API_KEY) {
      return res.status(500).json({ 
        error: 'Google Maps API key not configured'
      });
    }

    const photoUrl = `https://maps.googleapis.com/maps/api/place/photo?maxwidth=${maxwidth}&photo_reference=${photo_reference}&key=${GOOGLE_MAPS_API_KEY}`;

    res.json({
      success: true,
      data: {
        photo_url: photoUrl
      }
    });

  } catch (error) {
    console.error('Google Maps API Error:', error.message);
    res.status(500).json({ 
      error: 'Failed to generate photo URL',
      message: error.message
    });
  }
});

app.post('/geocode', async (req, res) => {
  try {
    const { address } = req.body;

    if (!GOOGLE_MAPS_API_KEY) {
      return res.status(500).json({ 
        error: 'Google Maps API key not configured'
      });
    }

    const response = await client.geocode({
      params: {
        address: address,
        key: GOOGLE_MAPS_API_KEY
      }
    });

    const result = response.data.results[0];

    res.json({
      success: true,
      data: {
        formatted_address: result.formatted_address,
        location: result.geometry.location,
        place_id: result.place_id,
        types: result.types
      }
    });

  } catch (error) {
    console.error('Google Maps API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to geocode address',
      message: error.response?.data?.error_message || error.message
    });
  }
});

app.post('/directions', async (req, res) => {
  try {
    const { origin, destination, mode = 'driving' } = req.body;

    if (!GOOGLE_MAPS_API_KEY) {
      return res.status(500).json({ 
        error: 'Google Maps API key not configured'
      });
    }

    const response = await client.directions({
      params: {
        origin: origin,
        destination: destination,
        mode: mode,
        key: GOOGLE_MAPS_API_KEY
      }
    });

    const route = response.data.routes[0];
    const leg = route.legs[0];

    res.json({
      success: true,
      data: {
        distance: leg.distance,
        duration: leg.duration,
        start_address: leg.start_address,
        end_address: leg.end_address,
        steps: leg.steps.map(step => ({
          distance: step.distance,
          duration: step.duration,
          instructions: step.html_instructions,
          travel_mode: step.travel_mode
        }))
      }
    });

  } catch (error) {
    console.error('Google Maps API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to get directions',
      message: error.response?.data?.error_message || error.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`🗺️  MCP Google Maps Server running on port ${PORT}`);
  console.log(`Google Maps API: ${GOOGLE_MAPS_API_KEY ? '✅ Configured' : '❌ Missing'}`);
});
