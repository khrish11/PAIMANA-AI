#!/usr/bin/env python
"""List all tables in the database."""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    tables = result.fetchall()
    print("Tables in paimana_ai database:")
    for table in tables:
        print(f"  - {table[0]}")
