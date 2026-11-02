# NC Plus One

A Python/PostgreSQL backend for managing events. Users can register, browse
events and RSVP; organisers can create events at venues and (planned) view
statistics about their audience.

> This is a backend-only project. There is no frontend.

---

## 🔗 Project architecture

![Database schema diagram showing users, venues, events and rsvps](image-1.png)

### Schema

| Table  | Columns |
|--------|---------|
| users  | user_id, email, password (bcrypt hash), name, created_at |
| venues | venue_id, name, address, capacity |
| events | event_id, title, description, starts_at, ends_at, organiser_id → users, venue_id → venues, created_at |
| rsvps  | rsvp_id, attendee_id → users, event_id → events, created_at; unique (attendee_id, event_id) |

---

## 🔗 Status

- [x] Database schema (users, venues, events, rsvps)
- [x] Seed data and seeding scripts
- [x] Data utilities, built with TDD (email normalisation, password hashing, event time validation)
- [x] `GET /api/events` with integration tests
- [ ] Remaining endpoints (single event, register, RSVP, manage attendance)
- [ ] Organiser features (create/manage events, audience statistics)

---

## 🔗 Tech

- Python 3.15 (developed and tested on 3.15.2), PostgreSQL
- FastAPI, uvicorn, Pydantic
- psycopg2, python-dotenv, bcrypt
- pytest, httpx, mypy

---

## 🔗 Project structure

```
app.py                  FastAPI application
main.py                 seeds the development database
config/connection.py    database connection
models/event.py         Pydantic response models
routers/events.py       event routes
src/seed.py             seeding functions
src/utils.py            data utilities (TDD)
scripts/seed_test.py    seeds the test database from tests/data/
db/drop_tables.sql      drops tables
db/create_tables.sql    creates tables
db/data/                development seed data (JSON)
db_model.erd.json       database diagram source
tests/                  pytest tests, fixtures and sample data (tests/data/)
pytest.toml             pytest configuration
mypy.ini                mypy configuration
.env.example            environment variable template
```

---

## 🔗 Setup

1. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create the development and test databases:

   ```bash
   createdb nc_plus_one
   createdb nc_plus_one_test
   ```

3. Create your environment file from the template, then replace the
   placeholder values with your own:

   ```bash
   cp .env.example .env.development
   ```

   | Variable     | Meaning                     |
   |--------------|-----------------------------|
   | `PGDATABASE` | Name of the database        |
   | `PGUSER`     | PostgreSQL username         |
   | `PGPASSWORD` | PostgreSQL password         |
   | `PGHOST`     | Database host (`localhost`) |

   `.env.development` is git-ignored; `.env.example` is committed.

---

## 🔗 Seeding the database

From the project root:

```bash
python main.py
```

This drops and recreates all tables, then loads `db/data/*.json`.
**It is destructive:** existing data is wiped.

Seeding is split into small functions in `src/seed.py`:

| Function            | Responsibility                                        |
|---------------------|-------------------------------------------------------|
| `drop_tables`       | Runs `db/drop_tables.sql` (children first)            |
| `create_tables`     | Runs `db/create_tables.sql` (parents first)           |
| `seed_users_table`  | Inserts users (emails normalised, passwords hashed)   |
| `seed_venues_table` | Inserts venues                                        |
| `seed_events_table` | Inserts events (end time validated)                   |
| `seed_rsvp_table`   | Inserts RSVPs                                         |
| `seed`              | Runs all of the above in order, rolling back on error |

Seed passwords in the JSON are plain-text dummy values; they are hashed with
bcrypt before being stored.

### Checking the data

```bash
psql nc_plus_one
```

```sql
\dt
SELECT event_id, title, starts_at FROM events ORDER BY starts_at;
```

---

## 🔗 Running the API

```bash
uvicorn app:app --reload
```

Interactive docs: <http://127.0.0.1:8000/docs>

### `GET /api/events`

Returns all events, soonest first.

```bash
curl http://127.0.0.1:8000/api/events
```

`200 OK`:

```json
{
  "events": [
    {
      "id": 1,
      "title": "Leeds Tech Meetup – June Edition",
      "starts_at": "2026-06-18T18:30:00+01:00",
      "ends_at": "2026-06-18T21:00:00+01:00",
      "location": "Nexus, Leeds, LS2 8PD"
    }
  ]
}
```

`location` is the venue name and address joined with a comma (just the name if
the venue has no address).

---

## 🔗 Utilities

`src/utils.py` holds functions that transform or validate data before
insertion. Each was built test-first (TDD):

- `normalise_email`: trims whitespace and lowercases
- `hash_password`: returns a salted bcrypt hash
- `validate_event_times`: rejects an event that ends before it starts on the same day

---

## 🔗 Testing

Run from the project root:

```bash
pytest -v
```

Tests use a separate database, `nc_plus_one_test`, seeded from a small set of
sample files in `tests/data/`, so development data is never touched.

- `tests/conftest.py` provides the fixtures: `sample_data`, `db` (seeds the
  test database once per run) and `client` (an API test client).
- `tests/test_utils.py` has unit tests for the utilities.
- `tests/test_events_api.py` has integration tests for `GET /api/events`.

The sample data is deliberately shuffled, with a start-time tie, an event that
crosses midnight and a venue with no address, so the ordering and location
logic are properly exercised.

To fill the test database by hand, for example to inspect it in `psql`:

```bash
python -m scripts.seed_test
```

### Type checking

```bash
mypy
```