"""
Database bootstrap check script.

Tests PostgreSQL connection and reports status.
"""
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings


def check_database():
    """Check database connection."""
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        print("DATABASE CONNECTION: OK")
        return True
        
    except Exception as e:
        print(f"DATABASE CONNECTION: FAILED")
        print(f"Reason: {str(e)}")
        return False


if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
