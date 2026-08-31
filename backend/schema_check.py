import os
from sqlalchemy import create_engine, inspect
from app.core.config import settings

engine = create_engine(settings.database_url)
inspector = inspect(engine)
tables = inspector.get_table_names()

required_tables = [
    "projects", "cuf_submissions", "reference_classes", "predictions",
    "risk_scores", "nid_results", "pbe_cohorts", "governance_actions",
    "model_registry", "positive_deviants", "extracted_actions",
    "playbooks", "playbook_suggestions"
]

missing = [t for t in required_tables if t not in tables]
print(f"Current tables: {tables}")
print(f"Missing required: {missing}")
if not missing:
    print("SCHEMA VERIFICATION OK")
else:
    print("SCHEMA VERIFICATION FAILED")
