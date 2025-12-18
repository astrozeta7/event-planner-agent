import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.database import get_db_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self, scraper_url: str, google_maps_url: str):
        self.scraper_url = scraper_url
        self.google_maps_url = google_maps_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.http_client.aclose()
    
    async def scrape_yelp_caterers(
        self, 
        location: str, 
        cuisine: Optional[str] = None, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            response = await self.http_client.post(
                f"{self.scraper_url}/scrape/yelp/caterers",
                json={
                    "location": location,
                    "cuisine": cuisine,
                    "limit": limit
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to scrape Yelp caterers: {e}")
            return []
    
    async def scrape_yelp_venues(
        self, 
        location: str, 
        capacity: Optional[int] = None, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            response = await self.http_client.post(
                f"{self.scraper_url}/scrape/yelp/venues",
                json={
                    "location": location,
                    "capacity": capacity,
                    "limit": limit
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to scrape Yelp venues: {e}")
            return []
    
    async def search_google_places(
        self, 
        query: str, 
        location: str, 
        place_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            response = await self.http_client.post(
                f"{self.google_maps_url}/places/search",
                json={
                    "query": query,
                    "location": location,
                    "type": place_type
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to search Google Places: {e}")
            return []
    
    async def ingest_caterer(self, caterer_data: Dict[str, Any]) -> Optional[str]:
        pool = await get_db_pool()
        
        try:
            query = """
                INSERT INTO caterers (
                    name, location, address, supported_cuisines,
                    base_price_per_guest, service_fee_flat, tax_rate_percent,
                    min_guests, max_guests, contact_phone,
                    external_id, external_source, external_url,
                    rating, review_count, price_level,
                    latitude, longitude, photos, business_status,
                    last_synced_at, is_active
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22
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
            
            cuisines = [caterer_data.get("cuisine_type", "General")]
            base_price = 50.0
            service_fee = 100.0
            tax_rate = 8.5
            min_guests = 10
            max_guests = 500
            
            result = await pool.fetchrow(
                query,
                caterer_data.get("name"),
                caterer_data.get("location"),
                caterer_data.get("address"),
                cuisines,
                base_price,
                service_fee,
                tax_rate,
                min_guests,
                max_guests,
                caterer_data.get("phone"),
                caterer_data.get("external_id"),
                caterer_data.get("source"),
                caterer_data.get("url"),
                caterer_data.get("rating"),
                caterer_data.get("review_count", 0),
                caterer_data.get("price_range"),
                caterer_data.get("coordinates", {}).get("latitude"),
                caterer_data.get("coordinates", {}).get("longitude"),
                caterer_data.get("photos", []),
                "OPERATIONAL" if not caterer_data.get("is_closed") else "CLOSED",
                datetime.utcnow(),
                not caterer_data.get("is_closed", False)
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
