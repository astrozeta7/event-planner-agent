import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_plan_event_success_with_multiple_matches():
    payload = {
        "event_date": "2025-09-15",
        "location": "San Francisco",
        "number_of_guests": 120,
        "cuisine_preferences": ["Italian", "Indian"],
        "budget_per_guest": 80,
        "event_type": "corporate",
        "needs_event_room": True,
        "special_requirements": "At least 10% vegetarian, nut-free options"
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "input_summary" in data
    assert "catering_analysis" in data
    assert "event_rooms" in data
    assert "summary_text" in data
    
    assert data["input_summary"]["location"] == "San Francisco"
    assert data["input_summary"]["number_of_guests"] == 120
    
    assert len(data["catering_analysis"]["by_cuisine"]) > 0
    
    assert len(data["event_rooms"]) > 0
    
    for room in data["event_rooms"]:
        assert room["capacity_min"] <= 120 <= room["capacity_max"]
        assert room["location"] == "San Francisco"


def test_plan_event_no_matching_location():
    payload = {
        "event_date": "2025-10-20",
        "location": "NonExistentCity",
        "number_of_guests": 100,
        "needs_event_room": True
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["catering_analysis"]["by_cuisine"]) == 0
    assert len(data["event_rooms"]) == 0
    assert "no catering services" in data["summary_text"].lower() or "unfortunately" in data["summary_text"].lower()


def test_plan_event_guest_count_exceeds_all_capacities():
    payload = {
        "event_date": "2025-11-10",
        "location": "San Francisco",
        "number_of_guests": 10000,
        "needs_event_room": True
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["event_rooms"]) == 0


def test_plan_event_missing_required_fields():
    payload = {
        "location": "San Francisco",
        "number_of_guests": 100
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 422


def test_plan_event_invalid_guest_count():
    payload = {
        "event_date": "2025-09-15",
        "location": "San Francisco",
        "number_of_guests": -10,
        "needs_event_room": False
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 422


def test_plan_event_without_event_room():
    payload = {
        "event_date": "2025-08-20",
        "location": "New York",
        "number_of_guests": 150,
        "cuisine_preferences": ["Italian"],
        "needs_event_room": False
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["event_rooms"]) == 0
    assert len(data["catering_analysis"]["by_cuisine"]) > 0


def test_plan_event_cost_breakdown_structure():
    payload = {
        "event_date": "2025-07-10",
        "location": "Los Angeles",
        "number_of_guests": 80,
        "cuisine_preferences": ["Mexican"],
        "needs_event_room": True
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data["catering_analysis"]["by_cuisine"]) > 0:
        cuisine_group = data["catering_analysis"]["by_cuisine"][0]
        assert "cuisine" in cuisine_group
        assert "providers" in cuisine_group
        
        if len(cuisine_group["providers"]) > 0:
            provider = cuisine_group["providers"][0]
            assert "cost_breakdown" in provider
            
            breakdown = provider["cost_breakdown"]
            assert "food_cost" in breakdown
            assert "service_fee" in breakdown
            assert "tax" in breakdown
            assert "total_cost" in breakdown
            assert "effective_cost_per_guest" in breakdown
            
            assert breakdown["total_cost"] == breakdown["food_cost"] + breakdown["service_fee"] + breakdown["tax"]


def test_plan_event_room_pricing_structure():
    payload = {
        "event_date": "2025-06-15",
        "location": "Chicago",
        "number_of_guests": 200,
        "needs_event_room": True
    }
    
    response = client.post("/plan-event", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    if len(data["event_rooms"]) > 0:
        room = data["event_rooms"][0]
        assert "pricing" in room
        
        pricing = room["pricing"]
        assert "base_room_rental_fee" in pricing
        assert "assumed_hours" in pricing
        assert "estimated_room_total_cost" in pricing
        
        assert pricing["assumed_hours"] == 4
