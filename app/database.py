import asyncpg
from typing import Optional, List, Dict, Any
import os
from contextlib import asynccontextmanager


class DatabaseConnection:
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://localhost:5432/event_planner_db'
            )
            cls._pool = await asyncpg.create_pool(
                database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
    
    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        pool = await cls.get_pool()
        async with pool.acquire() as connection:
            yield connection


class DatabaseService:
    @staticmethod
    async def execute_query(
        query: str,
        *args,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        async with DatabaseConnection.get_connection() as conn:
            if fetch_one:
                return await conn.fetchrow(query, *args)
            elif fetch_all:
                return await conn.fetch(query, *args)
            else:
                return await conn.execute(query, *args)
    
    @staticmethod
    async def fetch_venues(
        location: Optional[str] = None,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                id, name, location, address, capacity_min, capacity_max,
                base_room_rental_fee, hourly_rate, includes_catering,
                supported_cuisines_if_included, amenities, description,
                contact_email, contact_phone, is_active
            FROM venues
            WHERE is_active = TRUE
        """
        params = []
        param_count = 1
        
        if location:
            query += f" AND LOWER(location) = LOWER(${param_count})"
            params.append(location)
            param_count += 1
        
        if min_capacity is not None:
            query += f" AND capacity_max >= ${param_count}"
            params.append(min_capacity)
            param_count += 1
        
        if max_capacity is not None:
            query += f" AND capacity_min <= ${param_count}"
            params.append(max_capacity)
            param_count += 1
        
        query += " ORDER BY name"
        
        rows = await DatabaseService.execute_query(query, *params, fetch_all=True)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def fetch_caterers(
        location: Optional[str] = None,
        min_guests: Optional[int] = None,
        max_guests: Optional[int] = None,
        cuisines: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                id, name, location, address, supported_cuisines,
                base_price_per_guest, service_fee_flat, tax_rate_percent,
                min_guests, max_guests, notes, contact_email, contact_phone,
                is_active
            FROM caterers
            WHERE is_active = TRUE
        """
        params = []
        param_count = 1
        
        if location:
            query += f" AND LOWER(location) = LOWER(${param_count})"
            params.append(location)
            param_count += 1
        
        if min_guests is not None:
            query += f" AND max_guests >= ${param_count}"
            params.append(min_guests)
            param_count += 1
        
        if max_guests is not None:
            query += f" AND min_guests <= ${param_count}"
            params.append(max_guests)
            param_count += 1
        
        if cuisines:
            query += f" AND supported_cuisines && ${param_count}::text[]"
            params.append(cuisines)
            param_count += 1
        
        query += " ORDER BY name"
        
        rows = await DatabaseService.execute_query(query, *params, fetch_all=True)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def create_booking(
        client_id: str,
        venue_id: Optional[str],
        caterer_id: Optional[str],
        event_date: str,
        number_of_guests: int,
        event_type: Optional[str] = None,
        cuisine_preferences: Optional[List[str]] = None,
        special_requirements: Optional[str] = None,
        venue_cost: Optional[float] = None,
        catering_cost: Optional[float] = None,
        total_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        query = """
            INSERT INTO bookings (
                client_id, venue_id, caterer_id, event_date, number_of_guests,
                event_type, cuisine_preferences, special_requirements,
                venue_cost, catering_cost, total_cost, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'pending')
            RETURNING *
        """
        
        row = await DatabaseService.execute_query(
            query,
            client_id, venue_id, caterer_id, event_date, number_of_guests,
            event_type, cuisine_preferences, special_requirements,
            venue_cost, catering_cost, total_cost,
            fetch_one=True
        )
        
        return dict(row) if row else None
    
    @staticmethod
    async def check_venue_availability(venue_id: str, date: str) -> bool:
        query = """
            SELECT is_available
            FROM venue_availability
            WHERE venue_id = $1 AND date = $2
        """
        row = await DatabaseService.execute_query(query, venue_id, date, fetch_one=True)
        
        if row is None:
            return True
        
        return row['is_available']
    
    @staticmethod
    async def check_caterer_availability(caterer_id: str, date: str) -> bool:
        query = """
            SELECT is_available
            FROM caterer_availability
            WHERE caterer_id = $1 AND date = $2
        """
        row = await DatabaseService.execute_query(query, caterer_id, date, fetch_one=True)
        
        if row is None:
            return True
        
        return row['is_available']
