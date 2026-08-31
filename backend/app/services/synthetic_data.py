"""Synthetic/demo data adapter.

This module loads project data (from real PAIMANA Excel reports or the synthetic
seed generator) and feeds it through the SAME domain services used by the
PostgreSQL production path.

It does NOT duplicate business logic — it is purely a data-access layer.
"""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid5, UUID

import pandas as pd

from app.services.rcf_engine import fit_reference_class, size_band_for_cost

logger = logging.getLogger(__name__)

NAMESPACE = UUID("9f6b49ee-43b3-4a77-a55d-3c0b3afcc4a7")

# ─── Paths ────────────────────────────────────────────────────────────────────

_BASE = Path(__file__).resolve().parents[3]  # project root
_PAIMANA_EXCEL = _BASE / "data" / "REPORTS PAINAMA" / "Projects_Report (1).xlsx"
_SECTOR_EXCEL = _BASE / "data" / "REPORTS PAINAMA" / "Sector-Wise-Report.xlsx"
_COST_EXCEL = _BASE / "data" / "REPORTS PAINAMA" / "Cost-Wise-Report.xlsx"

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Multi State", "Delhi", "Jammu & Kashmir",
]


def _stable_id(label: str) -> str:
    return str(uuid5(NAMESPACE, label))


# ─── Data Loading ─────────────────────────────────────────────────────────────

_cache: dict[str, object] = {}


def _load_paimana_excel() -> pd.DataFrame:
    """Load the real PAIMANA Projects Report Excel."""
    if "paimana_raw" in _cache:
        return _cache["paimana_raw"]

    if not _PAIMANA_EXCEL.exists():
        logger.warning("PAIMANA Excel not found at %s; falling back to synthetic seed.", _PAIMANA_EXCEL)
        return pd.DataFrame()

    try:
        df = pd.read_excel(_PAIMANA_EXCEL, header=2, engine="openpyxl")
        df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
        df = df.dropna(subset=["Project Code"])
        _cache["paimana_raw"] = df
        logger.info("Loaded %d projects from PAIMANA Excel.", len(df))
        return df
    except Exception as exc:
        logger.error("Failed to load PAIMANA Excel: %s", exc)
        return pd.DataFrame()


def _parse_cost(val) -> float | None:
    """Parse cost values that may contain parenthetical revised costs."""
    if val is None or val == "" or val == 0:
        return None
    try:
        s = str(val).split("(")[0].strip().replace(",", "")
        return float(s)
    except (ValueError, TypeError):
        return None


def _parse_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    try:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(str(val).strip(), fmt).date()
            except ValueError:
                continue
    except Exception:
        pass
    return None


def _assign_state(row_data: dict, idx: int) -> str:
    """Assign a state — use real data if available, otherwise distribute."""
    # The Projects_Report doesn't have a state column, so we distribute
    return INDIAN_STATES[idx % len(INDIAN_STATES)]


def load_projects() -> list[dict]:
    """Load projects from PAIMANA Excel into a standardised dict format."""
    if "projects" in _cache:
        return _cache["projects"]

    raw = _load_paimana_excel()
    rng = random.Random(42)  # deterministic for demo

    if raw.empty:
        # Fall back to synthetic seed
        try:
            from data.seed.generate_synthetic_seed import generate
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                generate(Path(tmpdir), project_count=60, seed=20260828)
                projects_df = pd.read_csv(Path(tmpdir) / "projects.csv")
                submissions_df = pd.read_csv(Path(tmpdir) / "cuf_submissions.csv")
        except ImportError:
            # If data module is not available, return empty list
            logger.warning("Synthetic data module not available, returning empty projects list")
            return []

        projects = []
        for _, row in projects_df.iterrows():
            proj_subs = submissions_df[submissions_df["project_id"] == row["project_id"]]
            latest = proj_subs.sort_values("reporting_month").iloc[-1] if len(proj_subs) > 0 else None
            projects.append({
                "project_id": row["project_id"],
                "project_name": f"Synthetic Project {row['project_id'][:8]}",
                "sector": row["sector"],
                "ministry": row.get("ministry", "Synthetic Ministry"),
                "state": row["state"],
                "sanctioned_cost": float(row["sanctioned_cost"]),
                "revised_cost": float(latest["revised_cost"]) if latest is not None else float(row["sanctioned_cost"]),
                "expenditure": float(latest["expenditure"]) if latest is not None else 0,
                "physical_progress": float(latest["physical_progress"]) if latest is not None else 0,
                "approved_date": row["approved_date"],
                "planned_completion": str(latest["planned_completion"]) if latest is not None else "",
                "status": row["status"],
                "narrative_text": str(latest["narrative_text"]) if latest is not None else "",
                "submitted_by": str(latest.get("submitted_by", "synthetic-agency")) if latest is not None else "synthetic-agency",
                "reporting_month": str(latest["reporting_month"]) if latest is not None else "",
                "submitted_at": str(latest.get("submitted_at", "")) if latest is not None else "",
                "data_source": "synthetic_seed",
            })
        _cache["projects"] = projects
        return projects

    # Parse real PAIMANA data
    projects = []
    for idx, (_, row) in enumerate(raw.iterrows()):
        project_code = str(row.get("Project Code", "")).strip()
        if not project_code or project_code == "nan":
            continue

        project_id = _stable_id(f"paimana-{project_code}")
        sanctioned = _parse_cost(row.get("Original Cost (in cr.)")) or 0
        revised = _parse_cost(row.get("Revised Cost (in cr.)"))
        expenditure = _parse_cost(row.get("Expenditure (in cr.)"))
        progress_val = row.get("Physical Progress (in %)")
        progress = None
        if progress_val is not None:
            try:
                progress = float(str(progress_val).replace("%", "").strip())
            except (ValueError, TypeError):
                progress = None

        sanction_date = _parse_date(row.get("Sanction Date"))
        orig_completion = _parse_date(row.get("Original Date of Commissioning"))
        revised_completion = _parse_date(row.get("Revised Date of Commissioning"))

        sector = str(row.get("Sector Name", "Unknown")).strip()
        ministry = str(row.get("Line Ministry", "Unknown")).strip()
        project_name = str(row.get("Project Name", f"Project {project_code}")).strip()
        state = _assign_state(row, idx)

        # Determine status
        status_val = "active"
        if progress is not None and progress >= 99:
            status_val = "completed"

        # Generate synthetic submissions timeline for demo
        reporting_month = "2026-03-01"
        submitted_at = "2026-03-15T00:00:00+00:00"

        # Generate a narrative for NID testing
        narrative = _generate_narrative(
            project_name, progress, expenditure,
            revised or sanctioned, rng
        )

        projects.append({
            "project_id": project_id,
            "project_name": project_name[:120],
            "sector": sector,
            "ministry": ministry,
            "state": state,
            "sanctioned_cost": sanctioned,
            "revised_cost": revised if revised and revised > 0 else sanctioned,
            "expenditure": expenditure or 0,
            "physical_progress": progress or 0,
            "approved_date": sanction_date.isoformat() if sanction_date else "2020-01-01",
            "planned_completion": (revised_completion or orig_completion or date(2027, 12, 31)).isoformat(),
            "status": status_val,
            "narrative_text": narrative,
            "submitted_by": f"agency-{ministry[:20].lower().replace(' ', '_')}",
            "reporting_month": reporting_month,
            "submitted_at": submitted_at,
            "data_source": "paimana_excel_demo",
        })

    _cache["projects"] = projects
    logger.info("Parsed %d projects from PAIMANA Excel.", len(projects))
    return projects


def _generate_narrative(name: str, progress: float | None, expenditure: float | None,
                        cost: float, rng: random.Random) -> str:
    """Generate a demo narrative for NID testing."""
    templates = [
        f"Project '{name}' is progressing on track with {(progress or 0):.0f}% physical completion. "
        f"Total expenditure stands at ₹{(expenditure or 0):.2f} Cr against the project cost of ₹{cost:.2f} Cr.",

        f"Work on '{name}' continues as per schedule. Physical progress is reported at "
        f"{(progress or 0):.0f}%. No significant delays observed in the current reporting period.",

        f"The project '{name}' has achieved {(progress or 0):.0f}% completion. "
        f"Some procurement delays were noted but overall timeline remains manageable.",
    ]
    return rng.choice(templates)


def get_project_by_id(project_id: str) -> dict | None:
    """Get a single project by ID."""
    for p in load_projects():
        if p["project_id"] == project_id:
            return p
    return None


def get_completed_projects_df() -> pd.DataFrame:
    """Return completed projects as a DataFrame for RCF fitting."""
    if "completed_df" in _cache:
        return _cache["completed_df"]

    projects = load_projects()
    rng = random.Random(42)

    completed = [p for p in projects if p["status"] == "completed"]
    if len(completed) < 15:
        # Ensure we have enough for RCF by treating high-progress as "completed"
        for p in projects:
            if p["physical_progress"] >= 90 and p not in completed:
                completed.append(p)

    rows = []
    for p in completed:
        sanctioned = p["sanctioned_cost"]
        revised = p["revised_cost"]
        cost_overrun = revised / sanctioned if sanctioned > 0 else 1.0
        schedule_delay = rng.uniform(-2, max(0, (cost_overrun - 1) * 24 + rng.gauss(0, 3)))

        rows.append({
            "project_id": p["project_id"],
            "sector": p["sector"],
            "size_band": size_band_for_cost(sanctioned),
            "region": p["state"],
            "cost_overrun_ratio": cost_overrun,
            "schedule_delay_months": max(0, schedule_delay),
        })

    df = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["project_id", "sector", "size_band", "region", "cost_overrun_ratio", "schedule_delay_months"]
    )
    _cache["completed_df"] = df
    return df


def get_model_performance_data() -> list[dict]:
    """Return demo model performance metrics."""
    return [
        {
            "model_type": "Naive Baseline (Sector Avg)",
            "version": "v1.0-synthetic",
            "precision": 0.42, "recall": 0.65, "f1": 0.51,
            "roc_auc": 0.58, "pr_auc": 0.45, "brier_score": 0.28,
            "trained_date": "2026-08-01", "is_active": False,
            "sector_performance": {}, "notes": "Lower-bound reference.",
        },
        {
            "model_type": "Logistic Regression",
            "version": "v1.0-synthetic",
            "precision": 0.58, "recall": 0.72, "f1": 0.64,
            "roc_auc": 0.71, "pr_auc": 0.62, "brier_score": 0.22,
            "trained_date": "2026-08-01", "is_active": False,
            "sector_performance": {}, "notes": "Statistical baseline.",
        },
        {
            "model_type": "Random Forest",
            "version": "v1.0-synthetic",
            "precision": 0.68, "recall": 0.78, "f1": 0.73,
            "roc_auc": 0.82, "pr_auc": 0.75, "brier_score": 0.17,
            "trained_date": "2026-08-15", "is_active": True,
            "sector_performance": {"Roads & Highways": 0.85, "Railways": 0.79, "Coal": 0.76},
            "notes": "Primary ensemble model.",
        },
        {
            "model_type": "XGBoost",
            "version": "v1.0-synthetic",
            "precision": 0.71, "recall": 0.76, "f1": 0.73,
            "roc_auc": 0.84, "pr_auc": 0.77, "brier_score": 0.16,
            "trained_date": "2026-08-15", "is_active": False,
            "sector_performance": {"Roads & Highways": 0.87, "Railways": 0.81, "Coal": 0.78},
            "notes": "Ensemble candidate; pending Optuna tuning.",
        },
        {
            "model_type": "LightGBM",
            "version": "v1.0-synthetic",
            "precision": 0.69, "recall": 0.79, "f1": 0.74,
            "roc_auc": 0.83, "pr_auc": 0.76, "brier_score": 0.16,
            "trained_date": "2026-08-15", "is_active": False,
            "sector_performance": {"Roads & Highways": 0.86, "Railways": 0.80, "Coal": 0.77},
            "notes": "Ensemble candidate; pending Optuna tuning.",
        },
    ]


def clear_cache() -> None:
    """Clear the data cache (for testing)."""
    _cache.clear()
