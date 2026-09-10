#!/usr/bin/env python
"""List columns in key tables."""

from sqlalchemy import create_engine, text, inspect

DATABASE_URL = "postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai"

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

for table_name in ['cuf_submissions', 'projects', 'risk_scores', 'audit_log', 'data_refresh_log']:
    print(f"\n{table_name}:")
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
