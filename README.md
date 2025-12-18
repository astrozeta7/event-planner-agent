# Catering & Event Room Planning Agent

## Overview
A FastAPI-based service that helps plan events by analyzing catering services and event venues based on location, guest count, cuisine preferences, and budget.

## Features
- Cost estimation breakdown by cuisine, guest count, and location
- Event room availability and pricing
- Combined cost analysis for catering + venue
- Flexible filtering based on user requirements

## Quick Start

### Installation
```bash
cd event-planner-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the Service
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Interactive docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## API Usage

### Endpoint: `POST /plan-event`

#### Request Example
```bash
curl -X POST http://localhost:8000/plan-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_date": "2025-09-15",
    "location": "San Francisco",
    "number_of_guests": 120,
    "cuisine_preferences": ["Italian", "Indian"],
    "budget_per_guest": 80,
    "event_type": "corporate",
    "needs_event_room": true,
    "special_requirements": "At least 10% vegetarian, nut-free options"
  }'
```

#### Required Fields
- `event_date`: ISO date format (YYYY-MM-DD)
- `location`: City or region name
- `number_of_guests`: Positive integer

#### Optional Fields
- `cuisine_preferences`: List of cuisine types
- `budget_per_guest`: Budget per person
- `event_type`: Type of event (wedding, corporate, birthday, etc.)
- `needs_event_room`: Boolean (default: false)
- `special_requirements`: Dietary restrictions or special needs

#### Response Structure
```json
{
  "input_summary": { ... },
  "catering_analysis": {
    "by_cuisine": [ ... ]
  },
  "event_rooms": [ ... ],
  "summary_text": "..."
}
```

## Testing
```bash
pytest tests/
```

## Architecture
- **FastAPI**: REST API framework
- **Pydantic**: Data validation and serialization
- **In-memory data**: V1 uses mock data for catering services and venues
- **Service layer**: Separated business logic from API routing

## Future Enhancements (V2+)
- Database integration for persistent data
- Real-time availability checking
- Payment processing integration
- User authentication and booking management
- Email notifications
- Calendar integration
