"""Test database connection directly."""
import psycopg2

# Test 1: Connect via 127.0.0.1 (IPv4 only) with no password
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5435,
        user="paimana",
        dbname="paimana_ai"
    )
    print("DIRECT PSYCOPG2 CONNECTION (127.0.0.1, NO PASSWORD): OK")
    conn.close()
except Exception as e:
    print(f"DIRECT PSYCOPG2 CONNECTION (127.0.0.1, NO PASSWORD): FAILED - {e}")

# Test 2: Connect with password
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5435,
        user="paimana",
        password="paimanapass",
        dbname="paimana_ai"
    )
    print("DIRECT PSYCOPG2 CONNECTION (127.0.0.1, WITH PASSWORD): OK")
    conn.close()
except Exception as e:
    print(f"DIRECT PSYCOPG2 CONNECTION (127.0.0.1, WITH PASSWORD): FAILED - {e}")

# Test 3: SQLAlchemy with no password
try:
    from sqlalchemy import create_engine, text
    engine = create_engine("postgresql+psycopg2://paimana@127.0.0.1:5435/paimana_ai")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"SQLALCHEMY CONNECTION (127.0.0.1, NO PASSWORD): OK - {result.scalar()}")
except Exception as e:
    print(f"SQLALCHEMY CONNECTION (127.0.0.1, NO PASSWORD): FAILED - {e}")

# Test 4: SQLAlchemy with password
try:
    from sqlalchemy import create_engine, text
    engine = create_engine("postgresql+psycopg2://paimana:paimanapass@127.0.0.1:5435/paimana_ai")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"SQLALCHEMY CONNECTION (127.0.0.1, WITH PASSWORD): OK - {result.scalar()}")
except Exception as e:
    print(f"SQLALCHEMY CONNECTION (127.0.0.1, WITH PASSWORD): FAILED - {e}")

# Test 5: Try connecting via Unix socket (local)
try:
    conn = psycopg2.connect(
        user="paimana",
        dbname="paimana_ai"
    )
    print("DIRECT PSYCOPG2 CONNECTION (UNIX SOCKET): OK")
    conn.close()
except Exception as e:
    print(f"DIRECT PSYCOPG2 CONNECTION (UNIX SOCKET): FAILED - {e}")

# Test 6: Try connecting via Docker network hostname
try:
    conn = psycopg2.connect(
        host="db",
        port=5435,
        user="paimana",
        dbname="paimana_ai"
    )
    print("DIRECT PSYCOPG2 CONNECTION (DOCKER NETWORK): OK")
    conn.close()
except Exception as e:
    print(f"DIRECT PSYCOPG2 CONNECTION (DOCKER NETWORK): FAILED - {e}")
