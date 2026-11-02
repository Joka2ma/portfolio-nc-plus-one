"""Integration tests for GET/api/events/:id , using sample data"""

from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

EVENT_FIELDS = {
    "id","title","description","starts_at","ends_at",
    "location","address","capacity","created_at"
}

def get_event(client:TestClient,event_id:int)-> dict[str,Any]:
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    event:dict[str,any] = response.json()["event"]
    return event

def test_returns_200(client:TestClient)-> None:
    assert client.get("/api/events/2").status_code == 200
    
def test_body_is_object_with_event_key(client:TestClient) -> None:
    body = client.get("/api/events/2").json()
    assert list(body) == ["event"]
    assert isinstance(body["event"],dict)
    
def test_event_shape(client:TestClient) -> None:
    assert set(get_event(client,2)) == EVENT_FIELDS
    
    
def test_returns_matching_event(client:TestClient) -> None:
    event = get_event(client,2)
    assert event["id"] == 2
    assert event["title"] == "event_a"
    assert event["description"] == "description_a"
    
def test_times_are_the_seeded_instants(client:TestClient) -> None:
    event = get_event(client,2)
    assert datetime.fromisoformat(event["starts_at"]) == datetime.fromisoformat(
        "2026-03-03T10:00:00+00:00"
    )
    
    assert datetime.fromisoformat(event["ends_at"]) == datetime.fromisoformat(
        "2026-03-03T12:00:00+00:00"
    )

    
def test_includes_venue_details(client:TestClient) -> None:
    event = get_event(client,2)
    assert event["location"]== "venue_a"
    assert event["address"] == "address_a"
    assert event["capacity"] == 10

def test_venue_without_adddress_gives_null(client:TestClient) -> None:
    event = get_event(client,5)
    assert event["location"]== "venue_c"
    assert event["address"] is None
    assert event["capacity"] == 100  
    
    
def test_created_at_is_a_timestamp(client:TestClient) -> None:
    assert isinstance(datetime.fromisoformat(get_event(client,1)["created_at"]),datetime)
    
def test_every_listed_event_can_be_fetched_by_id(client: TestClient) -> None:
    listed = client.get("/api/events").json()["events"]
    for item in listed:
        event = get_event(client, item["id"])
        assert event["title"] == item["title"]


@pytest.mark.parametrize("event_id", ["999", "0", "-1", "99999999999999999999"])
def test_unknown_id_returns_404(client: TestClient, event_id: str) -> None:
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.parametrize("event_id", ["abc", "1.5", "2abc", "1_0", "1e3", "-"])
def test_invalid_id_returns_400(client: TestClient, event_id: str) -> None:
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 400
    assert "detail" in response.json()
