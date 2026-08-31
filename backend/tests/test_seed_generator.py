import csv
from pathlib import Path

from data.seed.generate_synthetic_seed import generate


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_seed_generator_marks_outputs_as_synthetic(tmp_path: Path) -> None:
    manifest = generate(tmp_path, project_count=30, seed=7)

    assert "Synthetic development data only" in manifest["limitation"]
    assert manifest["project_count"] == 30
    assert manifest["training_label_count"] == 15

    projects = read_rows(tmp_path / "projects.csv")
    submissions = read_rows(tmp_path / "cuf_submissions.csv")
    labels = read_rows(tmp_path / "synthetic_training_labels.csv")

    assert projects[0]["sector"].startswith("Synthetic")
    assert "not a PAIMANA" in submissions[0]["narrative_text"]
    assert labels[0]["label_source"] == "synthetic_demonstration_only_pending_real_data_audit"
