from typing import List
from app.models import VenueRoom, EventRoom, RoomPricing
from app.config import DEFAULT_EVENT_DURATION_HOURS


VENUE_ROOMS: List[VenueRoom] = [
    VenueRoom(
        id="room_sf_001",
        name="Bayview Ballroom",
        location="San Francisco",
        capacity_min=50,
        capacity_max=200,
        base_room_rental_fee=3000.0,
        hourly_rate=200.0,
        includes_catering=False,
        amenities=["AV equipment", "Stage", "Parking", "WiFi", "Dance floor"]
    ),
    VenueRoom(
        id="room_sf_002",
        name="Golden Gate Conference Center",
        location="San Francisco",
        capacity_min=100,
        capacity_max=500,
        base_room_rental_fee=5000.0,
        hourly_rate=300.0,
        includes_catering=True,
        supported_cuisines_if_included=["American", "Italian", "Asian Fusion"],
        amenities=["AV equipment", "Stage", "Parking", "WiFi", "Catering kitchen", "Green room"]
    ),
    VenueRoom(
        id="room_sf_003",
        name="Marina View Loft",
        location="San Francisco",
        capacity_min=30,
        capacity_max=120,
        base_room_rental_fee=2000.0,
        hourly_rate=150.0,
        includes_catering=False,
        amenities=["WiFi", "Parking", "Rooftop access", "City views"]
    ),
    VenueRoom(
        id="room_ny_001",
        name="Manhattan Grand Hall",
        location="New York",
        capacity_min=150,
        capacity_max=600,
        base_room_rental_fee=8000.0,
        hourly_rate=500.0,
        includes_catering=True,
        supported_cuisines_if_included=["Italian", "French", "American", "Fusion"],
        amenities=["AV equipment", "Stage", "Valet parking", "WiFi", "Crystal chandeliers", "Bridal suite"]
    ),
    VenueRoom(
        id="room_ny_002",
        name="Brooklyn Warehouse Space",
        location="New York",
        capacity_min=50,
        capacity_max=250,
        base_room_rental_fee=3500.0,
        hourly_rate=250.0,
        includes_catering=False,
        amenities=["WiFi", "Parking", "Industrial aesthetic", "Flexible layout"]
    ),
    VenueRoom(
        id="room_la_001",
        name="Hollywood Hills Estate",
        location="Los Angeles",
        capacity_min=80,
        capacity_max=300,
        base_room_rental_fee=6000.0,
        hourly_rate=400.0,
        includes_catering=False,
        amenities=["Pool area", "Garden", "Parking", "WiFi", "Outdoor kitchen", "Sunset views"]
    ),
    VenueRoom(
        id="room_la_002",
        name="Santa Monica Beach Club",
        location="Los Angeles",
        capacity_min=40,
        capacity_max=180,
        base_room_rental_fee=4000.0,
        hourly_rate=300.0,
        includes_catering=True,
        supported_cuisines_if_included=["Mexican", "American", "Seafood"],
        amenities=["Beach access", "Parking", "WiFi", "Outdoor seating", "Fire pits"]
    ),
    VenueRoom(
        id="room_chi_001",
        name="Chicago Skyline Tower",
        location="Chicago",
        capacity_min=100,
        capacity_max=400,
        base_room_rental_fee=5500.0,
        hourly_rate=350.0,
        includes_catering=False,
        amenities=["AV equipment", "Parking", "WiFi", "Panoramic views", "Multiple rooms"]
    ),
    VenueRoom(
        id="room_austin_001",
        name="Austin Music Hall",
        location="Austin",
        capacity_min=60,
        capacity_max=250,
        base_room_rental_fee=3000.0,
        hourly_rate=200.0,
        includes_catering=False,
        amenities=["Stage", "Sound system", "Parking", "WiFi", "Bar area", "Green room"]
    ),
    VenueRoom(
        id="room_austin_002",
        name="Hill Country Ranch Venue",
        location="Austin",
        capacity_min=50,
        capacity_max=300,
        base_room_rental_fee=4500.0,
        hourly_rate=250.0,
        includes_catering=True,
        supported_cuisines_if_included=["American", "BBQ", "Mexican"],
        amenities=["Outdoor space", "Parking", "WiFi", "Rustic barn", "Fire pit", "Lawn games"]
    )
]


def filter_event_rooms(
    location: str,
    number_of_guests: int
) -> List[VenueRoom]:
    filtered = []
    
    for room in VENUE_ROOMS:
        if room.location.lower() != location.lower():
            continue
        
        if not (room.capacity_min <= number_of_guests <= room.capacity_max):
            continue
        
        if not room.availability:
            continue
        
        filtered.append(room)
    
    return filtered


def calculate_room_cost(room: VenueRoom, duration_hours: int = DEFAULT_EVENT_DURATION_HOURS) -> float:
    base_cost = room.base_room_rental_fee
    
    if room.hourly_rate:
        hourly_cost = room.hourly_rate * duration_hours
        return base_cost + hourly_cost
    
    return base_cost


def build_event_room_response(
    rooms: List[VenueRoom],
    cheapest_catering_cost: float,
    duration_hours: int = DEFAULT_EVENT_DURATION_HOURS
) -> List[EventRoom]:
    event_rooms = []
    
    for room in rooms:
        room_total_cost = calculate_room_cost(room, duration_hours)
        
        pricing = RoomPricing(
            base_room_rental_fee=room.base_room_rental_fee,
            hourly_rate=room.hourly_rate,
            assumed_hours=duration_hours,
            estimated_room_total_cost=round(room_total_cost, 2)
        )
        
        combined_cost = None
        if not room.includes_catering and cheapest_catering_cost > 0:
            combined_cost = round(room_total_cost + cheapest_catering_cost, 2)
        
        event_room = EventRoom(
            room_id=room.id,
            room_name=room.name,
            location=room.location,
            capacity_min=room.capacity_min,
            capacity_max=room.capacity_max,
            amenities=room.amenities,
            pricing=pricing,
            includes_catering=room.includes_catering,
            supported_cuisines_if_included=room.supported_cuisines_if_included,
            estimated_combined_cost_with_cheapest_catering=combined_cost
        )
        
        event_rooms.append(event_room)
    
    event_rooms.sort(key=lambda x: x.pricing.estimated_room_total_cost)
    
    return event_rooms
