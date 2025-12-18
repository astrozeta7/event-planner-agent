from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date


class EventPlanRequest(BaseModel):
    event_date: str = Field(..., description="Event date in YYYY-MM-DD format")
    location: str = Field(..., description="City or region for the event")
    number_of_guests: int = Field(..., gt=0, description="Number of guests attending")
    cuisine_preferences: Optional[List[str]] = Field(default=None, description="Preferred cuisines")
    budget_per_guest: Optional[float] = Field(default=None, ge=0, description="Budget per guest")
    event_type: Optional[str] = Field(default=None, description="Type of event")
    needs_event_room: bool = Field(default=False, description="Whether an event room is needed")
    special_requirements: Optional[str] = Field(default=None, description="Special dietary or other requirements")

    @field_validator('event_date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError('event_date must be in YYYY-MM-DD format')
        return v


class CostBreakdown(BaseModel):
    food_cost: float
    service_fee: float
    tax: float
    total_cost: float
    effective_cost_per_guest: float


class CateringProvider(BaseModel):
    provider_id: str
    provider_name: str
    location: str
    cuisines: List[str]
    cost_breakdown: CostBreakdown
    notes: Optional[str] = None


class CuisineAnalysis(BaseModel):
    cuisine: str
    providers: List[CateringProvider]


class CateringAnalysis(BaseModel):
    by_cuisine: List[CuisineAnalysis]


class RoomPricing(BaseModel):
    base_room_rental_fee: float
    hourly_rate: Optional[float] = None
    assumed_hours: int
    estimated_room_total_cost: float


class EventRoom(BaseModel):
    room_id: str
    room_name: str
    location: str
    capacity_min: int
    capacity_max: int
    amenities: List[str]
    pricing: RoomPricing
    includes_catering: bool
    supported_cuisines_if_included: Optional[List[str]] = None
    estimated_combined_cost_with_cheapest_catering: Optional[float] = None


class InputSummary(BaseModel):
    event_date: str
    location: str
    number_of_guests: int
    cuisine_preferences: Optional[List[str]] = None
    budget_per_guest: Optional[float] = None


class EventPlanResponse(BaseModel):
    input_summary: InputSummary
    catering_analysis: CateringAnalysis
    event_rooms: List[EventRoom]
    summary_text: str


class CateringService(BaseModel):
    id: str
    name: str
    location: str
    supported_cuisines: List[str]
    base_price_per_guest: float
    service_fee_flat: float
    tax_rate_percent: float
    min_guests: int
    max_guests: int
    notes: Optional[str] = None


class VenueRoom(BaseModel):
    id: str
    name: str
    location: str
    capacity_min: int
    capacity_max: int
    base_room_rental_fee: float
    hourly_rate: Optional[float] = None
    includes_catering: bool
    supported_cuisines_if_included: Optional[List[str]] = None
    amenities: List[str]
    availability: bool = True
