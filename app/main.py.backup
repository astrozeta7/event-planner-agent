from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List

from app.models import (
    EventPlanRequest,
    EventPlanResponse,
    InputSummary,
    CateringAnalysis
)
from app.services.catering_service import (
    filter_catering_services,
    build_catering_analysis,
    get_cheapest_catering_cost
)
from app.services.venue_service import (
    filter_event_rooms,
    build_event_room_response
)
from app.config import DEFAULT_EVENT_DURATION_HOURS
from app.database import DatabaseConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseConnection.get_pool()
    yield
    await DatabaseConnection.close_pool()


app = FastAPI(
    title="Catering & Event Room Planning Agent V2",
    description="API for planning events with catering and venue recommendations - PostgreSQL powered",
    version="2.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "Catering & Event Room Planning Agent API V2",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "endpoints": {
            "plan_event": "POST /plan-event",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    try:
        pool = await DatabaseConnection.get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.post("/plan-event", response_model=EventPlanResponse)
async def plan_event(request: EventPlanRequest):
    try:
        filtered_catering = await filter_catering_services(
            location=request.location,
            number_of_guests=request.number_of_guests,
            cuisine_preferences=request.cuisine_preferences
        )

        catering_analysis = await build_catering_analysis(
            services=filtered_catering,
            number_of_guests=request.number_of_guests,
            cuisine_preferences=request.cuisine_preferences
        )

        event_rooms = []
        cheapest_catering_cost = 0.0

        if request.needs_event_room:
            filtered_rooms = await filter_event_rooms(
                location=request.location,
                number_of_guests=request.number_of_guests
            )

            cheapest_catering_cost = await get_cheapest_catering_cost(
                filtered_catering,
                request.number_of_guests
            )

            event_rooms = await build_event_room_response(
                rooms=filtered_rooms,
                cheapest_catering_cost=cheapest_catering_cost,
                duration_hours=DEFAULT_EVENT_DURATION_HOURS
            )
        
        summary_text = build_summary_text(
            location=request.location,
            event_date=request.event_date,
            number_of_guests=request.number_of_guests,
            catering_analysis=catering_analysis,
            event_rooms=event_rooms,
            cuisine_preferences=request.cuisine_preferences
        )
        
        input_summary = InputSummary(
            event_date=request.event_date,
            location=request.location,
            number_of_guests=request.number_of_guests,
            cuisine_preferences=request.cuisine_preferences,
            budget_per_guest=request.budget_per_guest
        )
        
        return EventPlanResponse(
            input_summary=input_summary,
            catering_analysis=catering_analysis,
            event_rooms=event_rooms,
            summary_text=summary_text
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def build_summary_text(
    location: str,
    event_date: str,
    number_of_guests: int,
    catering_analysis: CateringAnalysis,
    event_rooms: List,
    cuisine_preferences: List[str] = None
) -> str:
    if not catering_analysis.by_cuisine and not event_rooms:
        return (
            f"Unfortunately, we found no catering services or event rooms matching your requirements "
            f"for {number_of_guests} guests in {location} on {event_date}. "
            f"Please try a different location or adjust your guest count."
        )
    
    catering_summary = ""
    if catering_analysis.by_cuisine:
        total_providers = sum(len(c.providers) for c in catering_analysis.by_cuisine)
        cuisines_found = [c.cuisine for c in catering_analysis.by_cuisine]
        
        all_costs = []
        for cuisine_group in catering_analysis.by_cuisine:
            for provider in cuisine_group.providers:
                all_costs.append(provider.cost_breakdown.effective_cost_per_guest)
        
        min_cost = min(all_costs) if all_costs else 0
        max_cost = max(all_costs) if all_costs else 0
        
        cuisine_text = ", ".join(cuisines_found[:3])
        if len(cuisines_found) > 3:
            cuisine_text += f" and {len(cuisines_found) - 3} more"
        
        catering_summary = (
            f"Found {total_providers} catering provider(s) offering {cuisine_text} cuisine, "
            f"with per-guest costs ranging from ${min_cost:.2f} to ${max_cost:.2f}. "
        )
    else:
        catering_summary = f"No catering services found in {location}. "
    
    room_summary = ""
    if event_rooms:
        room_summary = f"{len(event_rooms)} event room(s) fit your capacity and location requirements."
    elif catering_analysis.by_cuisine:
        room_summary = "No event rooms available for your requirements."
    
    return (
        f"For {number_of_guests} guests in {location} on {event_date}: "
        f"{catering_summary}{room_summary}"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
