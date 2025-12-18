from typing import List, Dict
from app.models import CostBreakdown, CateringProvider, CuisineAnalysis, CateringAnalysis
from app.database import DatabaseService


async def filter_catering_services(
    location: str,
    number_of_guests: int,
    cuisine_preferences: List[str] = None
) -> List[Dict]:
    caterers = await DatabaseService.fetch_caterers(
        location=location,
        min_guests=number_of_guests,
        max_guests=number_of_guests,
        cuisines=cuisine_preferences
    )
    return caterers


def calculate_cost_breakdown(service: Dict, number_of_guests: int) -> CostBreakdown:
    food_cost = service['base_price_per_guest'] * number_of_guests
    service_fee = service['service_fee_flat']
    tax = (food_cost + service_fee) * (service['tax_rate_percent'] / 100)
    total_cost = food_cost + service_fee + tax
    effective_cost_per_guest = total_cost / number_of_guests

    return CostBreakdown(
        food_cost=round(float(food_cost), 2),
        service_fee=round(float(service_fee), 2),
        tax=round(float(tax), 2),
        total_cost=round(float(total_cost), 2),
        effective_cost_per_guest=round(float(effective_cost_per_guest), 2)
    )


async def build_catering_analysis(
    services: List[Dict],
    number_of_guests: int,
    cuisine_preferences: List[str] = None
) -> CateringAnalysis:
    cuisine_map: Dict[str, List[CateringProvider]] = {}

    for service in services:
        cost_breakdown = calculate_cost_breakdown(service, number_of_guests)

        provider = CateringProvider(
            provider_id=str(service['id']),
            provider_name=service['name'],
            location=service['location'],
            cuisines=service['supported_cuisines'],
            cost_breakdown=cost_breakdown,
            notes=service.get('notes')
        )

        for cuisine in service['supported_cuisines']:
            if cuisine_preferences:
                if not any(pref.lower() == cuisine.lower() for pref in cuisine_preferences):
                    continue

            if cuisine not in cuisine_map:
                cuisine_map[cuisine] = []
            cuisine_map[cuisine].append(provider)

    if not cuisine_map and services:
        for service in services:
            cost_breakdown = calculate_cost_breakdown(service, number_of_guests)
            provider = CateringProvider(
                provider_id=str(service['id']),
                provider_name=service['name'],
                location=service['location'],
                cuisines=service['supported_cuisines'],
                cost_breakdown=cost_breakdown,
                notes=service.get('notes')
            )
            for cuisine in service['supported_cuisines']:
                if cuisine not in cuisine_map:
                    cuisine_map[cuisine] = []
                cuisine_map[cuisine].append(provider)

    by_cuisine = [
        CuisineAnalysis(cuisine=cuisine, providers=providers)
        for cuisine, providers in cuisine_map.items()
    ]

    by_cuisine.sort(key=lambda x: x.cuisine)

    return CateringAnalysis(by_cuisine=by_cuisine)


async def get_cheapest_catering_cost(services: List[Dict], number_of_guests: int) -> float:
    if not services:
        return 0.0

    min_cost = float('inf')
    for service in services:
        breakdown = calculate_cost_breakdown(service, number_of_guests)
        if breakdown.total_cost < min_cost:
            min_cost = breakdown.total_cost

    return min_cost
