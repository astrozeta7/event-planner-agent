from typing import List, Dict
from app.models import CateringService, CostBreakdown, CateringProvider, CuisineAnalysis, CateringAnalysis


CATERING_SERVICES: List[CateringService] = [
    CateringService(
        id="cat_italian_001",
        name="La Bella Catering",
        location="San Francisco",
        supported_cuisines=["Italian"],
        base_price_per_guest=75.0,
        service_fee_flat=500.0,
        tax_rate_percent=9.5,
        min_guests=30,
        max_guests=250,
        notes="Halal-friendly options available, family recipes from Tuscany"
    ),
    CateringService(
        id="cat_indian_001",
        name="Spice Route Catering",
        location="San Francisco",
        supported_cuisines=["Indian"],
        base_price_per_guest=65.0,
        service_fee_flat=400.0,
        tax_rate_percent=9.5,
        min_guests=25,
        max_guests=300,
        notes="Authentic North and South Indian cuisine, vegan options available"
    ),
    CateringService(
        id="cat_fusion_001",
        name="Global Fusion Events",
        location="San Francisco",
        supported_cuisines=["Italian", "Indian", "Fusion", "Mediterranean"],
        base_price_per_guest=85.0,
        service_fee_flat=600.0,
        tax_rate_percent=9.5,
        min_guests=50,
        max_guests=200,
        notes="Award-winning fusion cuisine, customizable menus"
    ),
    CateringService(
        id="cat_italian_002",
        name="Mama Rosa's Catering",
        location="New York",
        supported_cuisines=["Italian", "American"],
        base_price_per_guest=70.0,
        service_fee_flat=450.0,
        tax_rate_percent=8.875,
        min_guests=40,
        max_guests=300,
        notes="Traditional Italian-American cuisine, gluten-free options"
    ),
    CateringService(
        id="cat_chinese_001",
        name="Golden Dragon Catering",
        location="San Francisco",
        supported_cuisines=["Chinese", "Asian Fusion"],
        base_price_per_guest=60.0,
        service_fee_flat=350.0,
        tax_rate_percent=9.5,
        min_guests=30,
        max_guests=400,
        notes="Dim sum specialists, nut-free options available"
    ),
    CateringService(
        id="cat_mexican_001",
        name="Fiesta Catering Co",
        location="Los Angeles",
        supported_cuisines=["Mexican", "Latin American"],
        base_price_per_guest=55.0,
        service_fee_flat=300.0,
        tax_rate_percent=9.5,
        min_guests=20,
        max_guests=500,
        notes="Authentic Mexican cuisine, taco bars, vegetarian-friendly"
    ),
    CateringService(
        id="cat_japanese_001",
        name="Sakura Catering Services",
        location="Los Angeles",
        supported_cuisines=["Japanese", "Asian Fusion"],
        base_price_per_guest=90.0,
        service_fee_flat=700.0,
        tax_rate_percent=9.5,
        min_guests=30,
        max_guests=150,
        notes="Sushi and hibachi specialists, premium ingredients"
    ),
    CateringService(
        id="cat_american_001",
        name="All-American Catering",
        location="Chicago",
        supported_cuisines=["American", "BBQ"],
        base_price_per_guest=65.0,
        service_fee_flat=400.0,
        tax_rate_percent=10.25,
        min_guests=50,
        max_guests=500,
        notes="BBQ, comfort food, farm-to-table options"
    ),
    CateringService(
        id="cat_indian_002",
        name="Taj Mahal Catering",
        location="New York",
        supported_cuisines=["Indian", "Pakistani"],
        base_price_per_guest=68.0,
        service_fee_flat=420.0,
        tax_rate_percent=8.875,
        min_guests=35,
        max_guests=250,
        notes="Halal certified, extensive vegetarian menu"
    ),
    CateringService(
        id="cat_mediterranean_001",
        name="Mediterranean Delights",
        location="Austin",
        supported_cuisines=["Mediterranean", "Greek", "Middle Eastern"],
        base_price_per_guest=72.0,
        service_fee_flat=450.0,
        tax_rate_percent=8.25,
        min_guests=30,
        max_guests=200,
        notes="Fresh ingredients, vegan and gluten-free options"
    )
]


def filter_catering_services(
    location: str,
    number_of_guests: int,
    cuisine_preferences: List[str] = None
) -> List[CateringService]:
    filtered = []
    
    for service in CATERING_SERVICES:
        if service.location.lower() != location.lower():
            continue
        
        if not (service.min_guests <= number_of_guests <= service.max_guests):
            continue
        
        if cuisine_preferences:
            has_matching_cuisine = any(
                pref.lower() in [c.lower() for c in service.supported_cuisines]
                for pref in cuisine_preferences
            )
            if not has_matching_cuisine:
                continue
        
        filtered.append(service)
    
    return filtered


def calculate_cost_breakdown(service: CateringService, number_of_guests: int) -> CostBreakdown:
    food_cost = service.base_price_per_guest * number_of_guests
    service_fee = service.service_fee_flat
    tax = (food_cost + service_fee) * (service.tax_rate_percent / 100)
    total_cost = food_cost + service_fee + tax
    effective_cost_per_guest = total_cost / number_of_guests
    
    return CostBreakdown(
        food_cost=round(food_cost, 2),
        service_fee=round(service_fee, 2),
        tax=round(tax, 2),
        total_cost=round(total_cost, 2),
        effective_cost_per_guest=round(effective_cost_per_guest, 2)
    )


def build_catering_analysis(
    services: List[CateringService],
    number_of_guests: int,
    cuisine_preferences: List[str] = None
) -> CateringAnalysis:
    cuisine_map: Dict[str, List[CateringProvider]] = {}
    
    for service in services:
        cost_breakdown = calculate_cost_breakdown(service, number_of_guests)
        
        provider = CateringProvider(
            provider_id=service.id,
            provider_name=service.name,
            location=service.location,
            cuisines=service.supported_cuisines,
            cost_breakdown=cost_breakdown,
            notes=service.notes
        )
        
        for cuisine in service.supported_cuisines:
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
                provider_id=service.id,
                provider_name=service.name,
                location=service.location,
                cuisines=service.supported_cuisines,
                cost_breakdown=cost_breakdown,
                notes=service.notes
            )
            for cuisine in service.supported_cuisines:
                if cuisine not in cuisine_map:
                    cuisine_map[cuisine] = []
                cuisine_map[cuisine].append(provider)
    
    by_cuisine = [
        CuisineAnalysis(cuisine=cuisine, providers=providers)
        for cuisine, providers in cuisine_map.items()
    ]
    
    by_cuisine.sort(key=lambda x: x.cuisine)
    
    return CateringAnalysis(by_cuisine=by_cuisine)


def get_cheapest_catering_cost(services: List[CateringService], number_of_guests: int) -> float:
    if not services:
        return 0.0
    
    min_cost = float('inf')
    for service in services:
        breakdown = calculate_cost_breakdown(service, number_of_guests)
        if breakdown.total_cost < min_cost:
            min_cost = breakdown.total_cost
    
    return min_cost
