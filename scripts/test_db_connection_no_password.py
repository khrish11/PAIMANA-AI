"""Test database connection without password (trust auth)."""
import psycopg

try:
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        user="paimana",
        dbname="paimana_ai"
    )
    print("DIRECT PSYCOPG CONNECTION (NO PASSWORD): OK")
    conn.close()
except Exception as e:
    print(f"DIRECT PSYCOPG CONNECTION (NO PASSWORD): FAILED - {e}")

try:
    from sqlalchemy import create_engine, text
    engine = create_engine("postgresql+psycopg://paimana@localhost:5432/paimana_ai")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"SQLALCHEMY CONNECTION (NO PASSWORD): OK - {result.scalar()}")
except Exception as e:
    print(f"SQLALCHEMY CONNECTION (NO PASSWORD): FAILED - {e}")
