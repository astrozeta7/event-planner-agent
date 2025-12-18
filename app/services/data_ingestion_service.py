import httpx
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from app.database import get_db_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self, scraper_url: str, google_maps_url: str):
        self.scraper_url = scraper_url
        self.google_maps_url = google_maps_url
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def scrape_osm_caterers(
        self,
        location: str,
        cuisine: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.scraper_url}/scrape/osm/caterers",
                    json={
                        "location": location,
                        "cuisine": cuisine,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("caterers", [])
        except Exception as e:
            logger.error(f"Failed to scrape OSM caterers: {e}")
            return []

    async def scrape_osm_venues(
        self,
        location: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.scraper_url}/scrape/osm/venues",
                    json={
                        "location": location,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("venues", [])
        except Exception as e:
            logger.error(f"Failed to scrape OSM venues: {e}")
            return []

    async def search_google_places(
        self,
        query: str,
        location: str,
        place_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.google_maps_url}/places/search",
                    json={
                        "query": query,
                        "location": location,
                        "type": place_type or "restaurant"
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"Failed to search Google Places: {e}")
            return []

    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.google_maps_url}/places/details/{place_id}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get place details: {e}")
            return {}

    async def ingest_caterer(self, caterer_data: Dict[str, Any]) -> Optional[str]:
        pool = await get_db_pool()

        try:
            query = """
                INSERT INTO caterers (
                    name, cuisine, address, phone, website, email,
                    external_id, external_source, external_url,
                    rating, review_count, price_level,
                    latitude, longitude, photos, business_status,
                    last_synced_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
                )
                ON CONFLICT (external_id, external_source)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    cuisine = EXCLUDED.cuisine,
                    address = EXCLUDED.address,
                    phone = EXCLUDED.phone,
                    website = EXCLUDED.website,
                    email = EXCLUDED.email,
                    rating = EXCLUDED.rating,
                    review_count = EXCLUDED.review_count,
                    price_level = EXCLUDED.price_level,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    photos = EXCLUDED.photos,
                    business_status = EXCLUDED.business_status,
                    last_synced_at = EXCLUDED.last_synced_at,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """

            result = await pool.fetchrow(
                query,
                caterer_data.get("name"),
                caterer_data.get("cuisine"),
                caterer_data.get("address"),
                caterer_data.get("phone"),
                caterer_data.get("website"),
                caterer_data.get("email"),
                caterer_data.get("external_id"),
                caterer_data.get("external_source"),
                caterer_data.get("external_url"),
                caterer_data.get("rating"),
                caterer_data.get("review_count", 0),
                caterer_data.get("price_level"),
                caterer_data.get("latitude"),
                caterer_data.get("longitude"),
                caterer_data.get("photos", []),
                caterer_data.get("business_status", "OPERATIONAL"),
                datetime.utcnow()
            )

            caterer_id = result["id"] if result else None
            logger.info(f"Ingested caterer: {caterer_data.get('name')} (ID: {caterer_id})")
            return str(caterer_id) if caterer_id else None

        except Exception as e:
            logger.error(f"Failed to ingest caterer {caterer_data.get('name')}: {e}")
            return None

    async def ingest_venue(self, venue_data: Dict[str, Any]) -> Optional[str]:
        pool = await get_db_pool()

        try:
            query = """
                INSERT INTO venues (
                    name, location, address, capacity_min, capacity_max,
                    base_room_rental_fee, hourly_rate, amenities,
                    contact_phone, external_id, external_source, external_url,
                    rating, review_count, price_level,
                    latitude, longitude, photos, business_status,
                    last_synced_at, is_active
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
                )
                ON CONFLICT (external_id, external_source)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    location = EXCLUDED.location,
                    address = EXCLUDED.address,
                    rating = EXCLUDED.rating,
                    review_count = EXCLUDED.review_count,
                    price_level = EXCLUDED.price_level,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    photos = EXCLUDED.photos,
                    business_status = EXCLUDED.business_status,
                    last_synced_at = EXCLUDED.last_synced_at,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """
            
            capacity = venue_data.get("capacity", 100)
            capacity_min = int(capacity * 0.5)
            capacity_max = capacity
            base_fee = venue_data.get("price_per_hour", 500)
            hourly_rate = base_fee
            amenities = venue_data.get("amenities", ["WiFi", "Parking"])
            
            result = await pool.fetchrow(
                query,
                venue_data.get("name"),
                venue_data.get("location"),
                venue_data.get("address"),
                capacity_min,
                capacity_max,
                base_fee,
                hourly_rate,
                amenities,
                venue_data.get("phone"),
                venue_data.get("external_id"),
                venue_data.get("source"),
                venue_data.get("url"),
                venue_data.get("rating"),
                venue_data.get("review_count", 0),
                venue_data.get("price_per_hour"),
                venue_data.get("coordinates", {}).get("latitude"),
                venue_data.get("coordinates", {}).get("longitude"),
                venue_data.get("photos", []),
                "OPERATIONAL" if not venue_data.get("is_closed") else "CLOSED",
                datetime.utcnow(),
                not venue_data.get("is_closed", False)
            )
            
            venue_id = result["id"] if result else None
            logger.info(f"Ingested venue: {venue_data.get('name')} (ID: {venue_id})")
            return str(venue_id) if venue_id else None
            
        except Exception as e:
            logger.error(f"Failed to ingest venue {venue_data.get('name')}: {e}")
            return None
    
    async def sync_caterers_for_location(
        self, 
        location: str, 
        cuisines: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Starting caterer sync for location: {location}")
        
        total_scraped = 0
        total_ingested = 0
        errors = []
        
        if cuisines:
            for cuisine in cuisines:
                caterers = await self.scrape_yelp_caterers(location, cuisine, limit=20)
                total_scraped += len(caterers)
                
                for caterer in caterers:
                    caterer_id = await self.ingest_caterer(caterer)
                    if caterer_id:
                        total_ingested += 1
                    else:
                        errors.append(f"Failed to ingest: {caterer.get('name')}")
        else:
            caterers = await self.scrape_yelp_caterers(location, limit=50)
            total_scraped = len(caterers)
            
            for caterer in caterers:
                caterer_id = await self.ingest_caterer(caterer)
                if caterer_id:
                    total_ingested += 1
                else:
                    errors.append(f"Failed to ingest: {caterer.get('name')}")
        
        logger.info(f"Caterer sync complete: {total_ingested}/{total_scraped} ingested")
        
        return {
            "location": location,
            "total_scraped": total_scraped,
            "total_ingested": total_ingested,
            "errors": errors
        }
    
    async def sync_venues_for_location(
        self, 
        location: str
    ) -> Dict[str, Any]:
        logger.info(f"Starting venue sync for location: {location}")
        
        venues = await self.scrape_yelp_venues(location, limit=50)
        total_scraped = len(venues)
        total_ingested = 0
        errors = []
        
        for venue in venues:
            venue_id = await self.ingest_venue(venue)
            if venue_id:
                total_ingested += 1
            else:
                errors.append(f"Failed to ingest: {venue.get('name')}")
        
        logger.info(f"Venue sync complete: {total_ingested}/{total_scraped} ingested")
        
        return {
            "location": location,
            "total_scraped": total_scraped,
            "total_ingested": total_ingested,
            "errors": errors
        }
