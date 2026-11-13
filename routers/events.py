"""Event routes."""

from typing import Any, cast

from fastapi import APIRouter, HTTPException,status
from psycopg2.extras import RealDictCursor

from config.connection import get_db_connection
from models.event import EventResponse, EventsResponse
from src.utils import parse_id

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventsResponse)
def get_events() -> dict[str, list[dict[str, Any]]]:
    """Return all events with their venue location, soonest first."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT e.event_id AS id,
                       e.title,
                       e.starts_at,
                       e.ends_at,
                       NULLIF(concat_ws(', ', v.name, v.address), '') AS location
                FROM events e
                LEFT JOIN venues v ON v.venue_id = e.venue_id
                ORDER BY e.starts_at ASC, e.event_id ASC;
                """
            )
            rows = cast(list[dict[str, Any]], cursor.fetchall())
            return {"events": rows}
    finally:
        conn.close()


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str) -> dict[str, dict[str, Any]]:
    """Return a single event, with its venue details.

    Raises:
        HTTPException: 400 if the id is not a valid integer, 404 if no event
            has that id.
    """
    try:
        parsed_id = parse_id(event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Event id must be an integer")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT e.event_id AS id,
                       e.title,
                       e.description,
                       e.starts_at,
                       e.ends_at,
                       v.name AS location,
                       v.address,
                       v.capacity,
                       e.created_at
                FROM events e
                LEFT JOIN venues v ON v.venue_id = e.venue_id
                WHERE e.event_id = %s;
                """,
                (parsed_id,),
            )
            row = cast(dict[str, Any] | None, cursor.fetchone())
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"event": row}