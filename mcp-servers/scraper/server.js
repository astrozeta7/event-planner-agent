import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3003;

app.use(cors());
app.use(express.json());

const OVERPASS_API_URL = 'https://overpass-api.de/api/interpreter';

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'mcp-scraper-osm' });
});

async function queryOverpass(query) {
  try {
    const response = await axios.post(OVERPASS_API_URL, `data=${encodeURIComponent(query)}`, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      timeout: 30000
    });
    return response.data;
  } catch (error) {
    console.error('Overpass API error:', error.message);
    throw error;
  }
}

function geocodeLocation(location) {
  const geocodes = {
    'san francisco': { lat: 37.7749, lon: -122.4194, radius: 10000 },
    'new york': { lat: 40.7128, lon: -74.0060, radius: 10000 },
    'los angeles': { lat: 34.0522, lon: -118.2437, radius: 10000 },
    'chicago': { lat: 41.8781, lon: -87.6298, radius: 10000 },
    'miami': { lat: 25.7617, lon: -80.1918, radius: 10000 },
    'seattle': { lat: 47.6062, lon: -122.3321, radius: 10000 },
    'boston': { lat: 42.3601, lon: -71.0589, radius: 10000 },
    'austin': { lat: 30.2672, lon: -97.7431, radius: 10000 },
    'denver': { lat: 39.7392, lon: -104.9903, radius: 10000 },
    'portland': { lat: 45.5152, lon: -122.6784, radius: 10000 }
  };

  const normalized = location.toLowerCase().trim();
  return geocodes[normalized] || { lat: 37.7749, lon: -122.4194, radius: 10000 };
}

app.post('/scrape/osm/caterers', async (req, res) => {
  try {
    const { location, cuisine, limit = 20 } = req.body;

    if (!location) {
      return res.status(400).json({ error: 'Location is required' });
    }

    const coords = geocodeLocation(location);

    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="restaurant"](around:${coords.radius},${coords.lat},${coords.lon});
        node["amenity"="cafe"](around:${coords.radius},${coords.lat},${coords.lon});
        node["amenity"="fast_food"](around:${coords.radius},${coords.lat},${coords.lon});
        node["shop"="catering"](around:${coords.radius},${coords.lat},${coords.lon});
        way["amenity"="restaurant"](around:${coords.radius},${coords.lat},${coords.lon});
        way["amenity"="cafe"](around:${coords.radius},${coords.lat},${coords.lon});
        way["shop"="catering"](around:${coords.radius},${coords.lat},${coords.lon});
      );
      out body;
      >;
      out skel qt;
    `;

    const data = await queryOverpass(query);

    const caterers = data.elements
      .filter(el => el.tags && el.tags.name)
      .slice(0, limit)
      .map(el => ({
        external_id: `osm_${el.id}`,
        external_source: 'openstreetmap',
        name: el.tags.name,
        cuisine: el.tags.cuisine || extractCuisineFromTags(el.tags) || 'General',
        address: formatOSMAddress(el.tags),
        phone: el.tags.phone || el.tags['contact:phone'] || null,
        website: el.tags.website || el.tags['contact:website'] || null,
        latitude: el.lat || (el.center ? el.center.lat : null),
        longitude: el.lon || (el.center ? el.center.lon : null),
        price_level: estimatePriceLevel(el.tags),
        rating: null,
        review_count: 0,
        business_status: 'OPERATIONAL',
        amenities: extractAmenitiesFromTags(el.tags),
        photos: [],
        opening_hours: el.tags.opening_hours || null
      }));

    res.json({
      success: true,
      source: 'openstreetmap',
      location,
      count: caterers.length,
      caterers
    });

  } catch (error) {
    console.error('OSM caterers scraping error:', error);
    res.status(500).json({
      error: 'Failed to scrape caterers from OpenStreetMap',
      message: error.message
    });
  }
});

app.post('/scrape/osm/venues', async (req, res) => {
  try {
    const { location, limit = 20 } = req.body;

    if (!location) {
      return res.status(400).json({ error: 'Location is required' });
    }

    const coords = geocodeLocation(location);

    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="conference_centre"](around:${coords.radius},${coords.lat},${coords.lon});
        node["amenity"="events_venue"](around:${coords.radius},${coords.lat},${coords.lon});
        node["amenity"="community_centre"](around:${coords.radius},${coords.lat},${coords.lon});
        node["tourism"="hotel"](around:${coords.radius},${coords.lat},${coords.lon});
        node["building"="hotel"](around:${coords.radius},${coords.lat},${coords.lon});
        way["amenity"="conference_centre"](around:${coords.radius},${coords.lat},${coords.lon});
        way["amenity"="events_venue"](around:${coords.radius},${coords.lat},${coords.lon});
        way["amenity"="community_centre"](around:${coords.radius},${coords.lat},${coords.lon});
        way["tourism"="hotel"](around:${coords.radius},${coords.lat},${coords.lon});
        way["building"="hotel"](around:${coords.radius},${coords.lat},${coords.lon});
      );
      out body;
      >;
      out skel qt;
    `;

    const data = await queryOverpass(query);

    const venues = data.elements
      .filter(el => el.tags && el.tags.name)
      .slice(0, limit)
      .map(el => ({
        external_id: `osm_${el.id}`,
        external_source: 'openstreetmap',
        name: el.tags.name,
        venue_type: determineVenueType(el.tags),
        address: formatOSMAddress(el.tags),
        phone: el.tags.phone || el.tags['contact:phone'] || null,
        website: el.tags.website || el.tags['contact:website'] || null,
        latitude: el.lat || (el.center ? el.center.lat : null),
        longitude: el.lon || (el.center ? el.center.lon : null),
        capacity: estimateCapacityFromTags(el.tags),
        price_level: estimatePriceLevel(el.tags),
        rating: null,
        review_count: 0,
        business_status: 'OPERATIONAL',
        amenities: extractAmenitiesFromTags(el.tags),
        photos: [],
        description: el.tags.description || null
      }));

    res.json({
      success: true,
      source: 'openstreetmap',
      location,
      count: venues.length,
      venues
    });

  } catch (error) {
    console.error('OSM venues scraping error:', error);
    res.status(500).json({
      error: 'Failed to scrape venues from OpenStreetMap',
      message: error.message
    });
  }
});

function extractCuisineFromTags(tags) {
  if (tags.cuisine) return tags.cuisine;
  if (tags['cuisine:type']) return tags['cuisine:type'];
  if (tags.amenity === 'fast_food') return 'Fast Food';
  if (tags.amenity === 'cafe') return 'Cafe';
  return null;
}

function formatOSMAddress(tags) {
  const parts = [];
  if (tags['addr:housenumber']) parts.push(tags['addr:housenumber']);
  if (tags['addr:street']) parts.push(tags['addr:street']);
  if (tags['addr:city']) parts.push(tags['addr:city']);
  if (tags['addr:state']) parts.push(tags['addr:state']);
  if (tags['addr:postcode']) parts.push(tags['addr:postcode']);

  return parts.length > 0 ? parts.join(', ') : null;
}

function estimatePriceLevel(tags) {
  if (tags['payment:cash'] === 'only') return 1;
  if (tags.stars) {
    const stars = parseInt(tags.stars);
    if (stars >= 4) return 4;
    if (stars >= 3) return 3;
    return 2;
  }
  return 2;
}

function estimateCapacityFromTags(tags) {
  if (tags.capacity) return parseInt(tags.capacity);
  if (tags.rooms) return parseInt(tags.rooms) * 2;
  if (tags.beds) return parseInt(tags.beds);
  if (tags.building === 'hotel') return 100;
  if (tags.amenity === 'conference_centre') return 500;
  if (tags.amenity === 'community_centre') return 200;
  return 50;
}

function determineVenueType(tags) {
  if (tags.amenity === 'conference_centre') return 'Conference Center';
  if (tags.amenity === 'events_venue') return 'Event Space';
  if (tags.amenity === 'community_centre') return 'Community Center';
  if (tags.tourism === 'hotel' || tags.building === 'hotel') return 'Hotel';
  return 'Event Venue';
}

function extractAmenitiesFromTags(tags) {
  const amenities = [];

  if (tags.wheelchair === 'yes') amenities.push('Wheelchair Accessible');
  if (tags.wifi === 'yes' || tags['internet_access'] === 'wlan') amenities.push('WiFi');
  if (tags.parking === 'yes' || tags['parking:fee']) amenities.push('Parking');
  if (tags.air_conditioning === 'yes') amenities.push('Air Conditioning');
  if (tags.outdoor_seating === 'yes') amenities.push('Outdoor Seating');
  if (tags.takeaway === 'yes') amenities.push('Takeaway');
  if (tags.delivery === 'yes') amenities.push('Delivery');
  if (tags['payment:credit_cards'] === 'yes') amenities.push('Credit Cards Accepted');

  return amenities;
}

function extractCuisineFromCategories(categories) {
  if (!categories || categories.length === 0) return 'General';

  const cuisineMap = {
    'italian': 'Italian',
    'mexican': 'Mexican',
    'chinese': 'Chinese',
    'japanese': 'Japanese',
    'indian': 'Indian',
    'mediterranean': 'Mediterranean',
    'american': 'American',
    'french': 'French',
    'thai': 'Thai',
    'korean': 'Korean'
  };

  for (const category of categories) {
    const alias = category.alias.toLowerCase();
    for (const [key, value] of Object.entries(cuisineMap)) {
      if (alias.includes(key)) {
        return value;
      }
    }
  }

  return categories[0].title;
}

function formatAddress(location) {
  const parts = [
    location.address1,
    location.city,
    location.state,
    location.zip_code
  ].filter(Boolean);
  
  return parts.join(', ');
}

function estimateCapacity(business) {
  const priceLevel = business.price?.length || 2;
  
  if (priceLevel === 1) return 50;
  if (priceLevel === 2) return 100;
  if (priceLevel === 3) return 200;
  return 300;
}

function estimatePricing(priceLevel) {
  const pricingMap = {
    '$': 100,
    '$$': 250,
    '$$$': 500,
    '$$$$': 1000
  };
  
  return pricingMap[priceLevel] || 250;
}

function extractAmenities(categories) {
  const amenityKeywords = ['wifi', 'parking', 'outdoor', 'bar', 'kitchen', 'av', 'stage'];
  const amenities = [];

  categories.forEach(category => {
    const title = category.title.toLowerCase();
    amenityKeywords.forEach(keyword => {
      if (title.includes(keyword)) {
        amenities.push(keyword);
      }
    });
  });

  return amenities.length > 0 ? amenities : ['WiFi', 'Parking'];
}

app.listen(PORT, () => {
  console.log(`🔍 MCP Scraper Server running on port ${PORT}`);
  console.log(`✅ OpenStreetMap Overpass API - No API key needed!`);
});