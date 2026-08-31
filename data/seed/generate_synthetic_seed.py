from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID, uuid5

NAMESPACE = UUID("9f6b49ee-43b3-4a77-a55d-3c0b3afcc4a7")

SYNTHETIC_SECTORS = [
    "Synthetic Sector A",
    "Synthetic Sector B",
    "Synthetic Sector C",
    "Synthetic Sector D",
]
SYNTHETIC_MINISTRIES = [
    "Synthetic Ministry A",
    "Synthetic Ministry B",
    "Synthetic Ministry C",
]
SYNTHETIC_STATES = [
    "Synthetic State A",
    "Synthetic State B",
    "Synthetic State C",
    "Synthetic State D",
    "Synthetic State E",
]


def stable_uuid(label: str) -> str:
    return str(uuid5(NAMESPACE, label))


def add_months(value: date, months: int) -> date:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, 28)
    return date(year, month, day)


def project_rows(project_count: int, rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(project_count):
        project_id = stable_uuid(f"synthetic-project-{index:03d}")
        sanctioned_cost = rng.choice([180, 260, 420, 760, 1350, 2250, 3800])
        approved = add_months(date(2018, 1, 1), index * 2)
        rows.append(
            {
                "project_id": project_id,
                "sector": SYNTHETIC_SECTORS[index % len(SYNTHETIC_SECTORS)],
                "ministry": SYNTHETIC_MINISTRIES[index % len(SYNTHETIC_MINISTRIES)],
                "state": SYNTHETIC_STATES[index % len(SYNTHETIC_STATES)],
                "sanctioned_cost": f"{sanctioned_cost:.2f}",
                "approved_date": approved.isoformat(),
                "status": "completed" if index < project_count // 2 else "active",
            }
        )
    return rows


def cuf_submission_rows(projects: list[dict[str, object]], rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for project_index, project in enumerate(projects):
        approved = date.fromisoformat(str(project["approved_date"]))
        sanctioned_cost = float(project["sanctioned_cost"])
        reporting_months = 18 if project["status"] == "completed" else 12
        target_overrun = rng.uniform(-0.04, 0.28)
        final_revised_cost = sanctioned_cost * (1 + target_overrun)

        for month in range(reporting_months):
            reporting_month = add_months(approved, month + 1)
            progress = min(100.0, max(0.0, (month + 1) / reporting_months * 100 + rng.uniform(-4, 4)))
            spend_fraction = min(1.15, max(0.0, progress / 100 + rng.uniform(-0.08, 0.12)))
            revised_cost = sanctioned_cost + ((final_revised_cost - sanctioned_cost) * (month + 1) / reporting_months)
            submission_id = stable_uuid(f"{project['project_id']}-{reporting_month.isoformat()}")
            rows.append(
                {
                    "submission_id": submission_id,
                    "project_id": project["project_id"],
                    "reporting_month": reporting_month.isoformat(),
                    "revised_cost": f"{revised_cost:.2f}",
                    "expenditure": f"{revised_cost * spend_fraction:.2f}",
                    "physical_progress": f"{progress:.2f}",
                    "planned_completion": add_months(approved, reporting_months).isoformat(),
                    "narrative_text": (
                        "Synthetic narrative for local development only; "
                        "not a PAIMANA, CUF, OCMS, or government record."
                    ),
                    "submitted_by": f"synthetic-agency-{project_index % 5}",
                    "submitted_at": datetime(
                        reporting_month.year, reporting_month.month, 15, tzinfo=timezone.utc
                    ).isoformat(),
                }
            )
    return rows


def training_label_rows(
    projects: list[dict[str, object]], submissions: list[dict[str, object]]
) -> list[dict[str, object]]:
    latest_submission_by_project: dict[str, dict[str, object]] = {}
    for submission in submissions:
        latest_submission_by_project[str(submission["project_id"])] = submission

    rows: list[dict[str, object]] = []
    for project in projects:
        if project["status"] != "completed":
            continue
        latest = latest_submission_by_project[str(project["project_id"])]
        sanctioned = float(project["sanctioned_cost"])
        revised = float(latest["revised_cost"])
        cost_overrun_ratio = revised / sanctioned - 1
        approved = date.fromisoformat(str(project["approved_date"]))
        planned = date.fromisoformat(str(latest["planned_completion"]))
        months_planned = (planned.year - approved.year) * 12 + planned.month - approved.month
        synthetic_delay = max(0, int(round(cost_overrun_ratio * 18)))
        rows.append(
            {
                "project_id": project["project_id"],
                "synthetic_actual_final_cost": f"{revised:.2f}",
                "synthetic_actual_completion_date": add_months(planned, synthetic_delay).isoformat(),
                "cost_overrun_ratio": f"{cost_overrun_ratio:.4f}",
                "schedule_delay_months": synthetic_delay,
                "cost_overrun_gt_10": int(cost_overrun_ratio > 0.10),
                "schedule_delay_gt_6m": int(synthetic_delay > 6),
                "label_source": "synthetic_demonstration_only_pending_real_data_audit",
                "planned_duration_months": months_planned,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows generated for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate(output_dir: Path, project_count: int = 48, seed: int = 20260828) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    projects = project_rows(project_count, rng)
    submissions = cuf_submission_rows(projects, rng)
    labels = training_label_rows(projects, submissions)

    write_csv(output_dir / "projects.csv", projects)
    write_csv(output_dir / "cuf_submissions.csv", submissions)
    write_csv(output_dir / "synthetic_training_labels.csv", labels)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "project_count": len(projects),
        "submission_count": len(submissions),
        "training_label_count": len(labels),
        "limitation": (
            "Synthetic development data only. These records are not PAIMANA, CUF, OCMS, "
            "MoSPI, or other government data and must not be used for claimed model accuracy."
        ),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PAIMANA-AI synthetic development data.")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "generated")
    parser.add_argument("--project-count", type=int, default=48)
    parser.add_argument("--seed", type=int, default=20260828)
    args = parser.parse_args()

    if args.project_count < 30:
        raise SystemExit("project-count must be at least 30 so RCF fallback paths can be exercised.")

    manifest = generate(args.output_dir, args.project_count, args.seed)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
