from typing import List, Dict
from app.models import EventRoom, RoomPricing
from app.config import DEFAULT_EVENT_DURATION_HOURS
from app.database import DatabaseService


async def filter_event_rooms(
    location: str,
    number_of_guests: int
) -> List[Dict]:
    venues = await DatabaseService.fetch_venues(
        location=location,
        min_capacity=number_of_guests,
        max_capacity=number_of_guests
    )
    return venues


def calculate_room_cost(room: Dict, duration_hours: int = DEFAULT_EVENT_DURATION_HOURS) -> float:
    base_cost = room['base_room_rental_fee']

    if room.get('hourly_rate'):
        hourly_cost = room['hourly_rate'] * duration_hours
        return float(base_cost + hourly_cost)

    return float(base_cost)


async def build_event_room_response(
    rooms: List[Dict],
    cheapest_catering_cost: float,
    duration_hours: int = DEFAULT_EVENT_DURATION_HOURS
) -> List[EventRoom]:
    event_rooms = []

    for room in rooms:
        room_total_cost = calculate_room_cost(room, duration_hours)

        pricing = RoomPricing(
            base_room_rental_fee=float(room['base_room_rental_fee']),
            hourly_rate=float(room['hourly_rate']) if room.get('hourly_rate') else None,
            assumed_hours=duration_hours,
            estimated_room_total_cost=round(room_total_cost, 2)
        )

        combined_cost = None
        if not room['includes_catering'] and cheapest_catering_cost > 0:
            combined_cost = round(room_total_cost + cheapest_catering_cost, 2)

        event_room = EventRoom(
            room_id=str(room['id']),
            room_name=room['name'],
            location=room['location'],
            capacity_min=room['capacity_min'],
            capacity_max=room['capacity_max'],
            amenities=room['amenities'],
            pricing=pricing,
            includes_catering=room['includes_catering'],
            supported_cuisines_if_included=room.get('supported_cuisines_if_included'),
            estimated_combined_cost_with_cheapest_catering=combined_cost
        )

        event_rooms.append(event_room)

    event_rooms.sort(key=lambda x: x.pricing.estimated_room_total_cost)

    return event_rooms
