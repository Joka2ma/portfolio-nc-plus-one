# config/connection.py
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as PGConnection
from collections import Generator

load_dotenv("ENV_FILE",".env.development")


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "nc_plus_one"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
    )

def get_db() -> Generator[PgConnection, None, None]:
    """Provide a database connection per request and close it afterward."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
