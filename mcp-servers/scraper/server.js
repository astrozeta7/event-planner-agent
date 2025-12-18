import express from 'express';
import axios from 'axios';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3003;

app.use(cors());
app.use(express.json());

const YELP_API_KEY = process.env.YELP_API_KEY;
const YELP_API_BASE = 'https://api.yelp.com/v3';

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'mcp-scraper-server',
    apis: {
      yelp: YELP_API_KEY ? 'configured' : 'missing'
    }
  });
});

app.post('/scrape/yelp/caterers', async (req, res) => {
  try {
    const { location, cuisine, limit = 20 } = req.body;

    if (!YELP_API_KEY) {
      return res.status(500).json({ 
        error: 'Yelp API key not configured',
        message: 'Please set YELP_API_KEY in environment variables'
      });
    }

    const searchTerm = cuisine ? `${cuisine} catering` : 'catering';
    
    const response = await axios.get(`${YELP_API_BASE}/businesses/search`, {
      headers: {
        'Authorization': `Bearer ${YELP_API_KEY}`
      },
      params: {
        term: searchTerm,
        location: location,
        categories: 'caterers,restaurants',
        limit: limit,
        sort_by: 'rating'
      }
    });

    const caterers = response.data.businesses.map(business => ({
      external_id: business.id,
      name: business.name,
      cuisine_type: cuisine || extractCuisineFromCategories(business.categories),
      location: business.location.city,
      address: formatAddress(business.location),
      rating: business.rating,
      review_count: business.review_count,
      price_range: business.price || '$$',
      phone: business.phone,
      image_url: business.image_url,
      url: business.url,
      coordinates: business.coordinates,
      is_closed: business.is_closed,
      source: 'yelp',
      last_updated: new Date().toISOString()
    }));

    res.json({
      success: true,
      count: caterers.length,
      data: caterers,
      metadata: {
        location: location,
        cuisine: cuisine,
        source: 'yelp_fusion_api'
      }
    });

  } catch (error) {
    console.error('Yelp API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to scrape Yelp caterers',
      message: error.response?.data?.error?.description || error.message
    });
  }
});

app.post('/scrape/yelp/venues', async (req, res) => {
  try {
    const { location, capacity, limit = 20 } = req.body;

    if (!YELP_API_KEY) {
      return res.status(500).json({ 
        error: 'Yelp API key not configured',
        message: 'Please set YELP_API_KEY in environment variables'
      });
    }

    const response = await axios.get(`${YELP_API_BASE}/businesses/search`, {
      headers: {
        'Authorization': `Bearer ${YELP_API_KEY}`
      },
      params: {
        term: 'event venue',
        location: location,
        categories: 'venues,eventservices',
        limit: limit,
        sort_by: 'rating'
      }
    });

    const venues = response.data.businesses.map(business => ({
      external_id: business.id,
      name: business.name,
      location: business.location.city,
      address: formatAddress(business.location),
      capacity: estimateCapacity(business),
      rating: business.rating,
      review_count: business.review_count,
      price_per_hour: estimatePricing(business.price),
      amenities: extractAmenities(business.categories),
      phone: business.phone,
      image_url: business.image_url,
      url: business.url,
      coordinates: business.coordinates,
      is_closed: business.is_closed,
      source: 'yelp',
      last_updated: new Date().toISOString()
    }));

    res.json({
      success: true,
      count: venues.length,
      data: venues,
      metadata: {
        location: location,
        capacity: capacity,
        source: 'yelp_fusion_api'
      }
    });

  } catch (error) {
    console.error('Yelp API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to scrape Yelp venues',
      message: error.response?.data?.error?.description || error.message
    });
  }
});

app.post('/scrape/yelp/business/:id', async (req, res) => {
  try {
    const { id } = req.params;

    if (!YELP_API_KEY) {
      return res.status(500).json({ 
        error: 'Yelp API key not configured'
      });
    }

    const response = await axios.get(`${YELP_API_BASE}/businesses/${id}`, {
      headers: {
        'Authorization': `Bearer ${YELP_API_KEY}`
      }
    });

    const reviewsResponse = await axios.get(`${YELP_API_BASE}/businesses/${id}/reviews`, {
      headers: {
        'Authorization': `Bearer ${YELP_API_KEY}`
      }
    });

    res.json({
      success: true,
      data: {
        business: response.data,
        reviews: reviewsResponse.data.reviews
      }
    });

  } catch (error) {
    console.error('Yelp API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to fetch business details',
      message: error.response?.data?.error?.description || error.message
    });
  }
});

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
  console.log(`Yelp API: ${YELP_API_KEY ? '✅ Configured' : '❌ Missing'}`);
});
