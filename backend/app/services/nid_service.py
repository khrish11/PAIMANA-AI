"""Narrative Inconsistency Detector (NID) service.

Pipeline:
    LLM claim extraction → Pydantic structured output → deterministic cross-check → NQC score

The LLM does NOT directly determine the numeric risk score.
On Ollama unavailability, returns NID unavailable gracefully.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NIDContradictionResult:
    claim: str
    referenced_cuf_field: str
    expected_value: str
    actual_value: str
    coherence_score: float
    severity: str
    explanation: str


@dataclass(frozen=True)
class NIDResult:
    status: str  # "available", "unavailable", "partial"
    nqc_score: float | None
    confidence: str | None
    extracted_claims: list[str]
    contradictions: list[NIDContradictionResult]
    model_version: str
    prompt_version: str
    error_message: str | None


# ─── Deterministic claim extraction (fallback when LLM unavailable) ──────────

NUMBER_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent|crore|cr|lakh|months?|days?)")
PROGRESS_PATTERN = re.compile(r"(?:progress|completion|completed?)\s+(?:is\s+)?(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)
COST_PATTERN = re.compile(r"(?:cost|expenditure|expense|spent?)\s+.*?(\d+(?:\.\d+)?)\s*(?:crore|cr)", re.IGNORECASE)
DELAY_PATTERN = re.compile(r"(?:delay|behind|slip)\s+.*?(\d+(?:\.\d+)?)\s*(?:months?|weeks?)", re.IGNORECASE)
ON_TRACK_PATTERN = re.compile(r"(?:on\s+track|on\s+schedule|ahead\s+of\s+schedule|no\s+delay)", re.IGNORECASE)


def _extract_claims_rule_based(narrative: str) -> list[str]:
    """Extract simple claims from narrative text using regex patterns."""
    claims: list[str] = []

    for match in PROGRESS_PATTERN.finditer(narrative):
        claims.append(f"Narrative claims progress is {match.group(1)}%")

    for match in COST_PATTERN.finditer(narrative):
        claims.append(f"Narrative mentions cost/expenditure of ₹{match.group(1)} Cr")

    for match in DELAY_PATTERN.finditer(narrative):
        claims.append(f"Narrative mentions delay of {match.group(1)} months")

    if ON_TRACK_PATTERN.search(narrative):
        claims.append("Narrative claims project is on track / on schedule")

    if not claims:
        claims.append("No specific quantitative claims detected in narrative")

    return claims


def _cross_check_claims(
    claims: list[str],
    *,
    actual_progress: float | None,
    actual_cost: float | None,
    actual_schedule_slip: float | None,
) -> list[NIDContradictionResult]:
    """Deterministic cross-check of extracted claims against CUF fields."""
    contradictions: list[NIDContradictionResult] = []

    for claim in claims:
        progress_match = re.search(r"progress is (\d+(?:\.\d+)?)%", claim)
        if progress_match and actual_progress is not None:
            claimed = float(progress_match.group(1))
            diff = abs(claimed - actual_progress)
            if diff > 10:
                severity = "CRITICAL" if diff > 25 else ("HIGH" if diff > 15 else "MODERATE")
                contradictions.append(NIDContradictionResult(
                    claim=claim,
                    referenced_cuf_field="physical_progress",
                    expected_value=f"{claimed}%",
                    actual_value=f"{actual_progress}%",
                    coherence_score=round(max(0, 1 - diff / 100), 2),
                    severity=severity,
                    explanation=(
                        f"Narrative claims {claimed}% progress, but CUF physical_progress "
                        f"field reports {actual_progress}%. Difference of {diff:.1f}%."
                    ),
                ))

        if "on track" in claim.lower() or "on schedule" in claim.lower():
            if actual_schedule_slip is not None and actual_schedule_slip > 3:
                contradictions.append(NIDContradictionResult(
                    claim=claim,
                    referenced_cuf_field="schedule_slip_months",
                    expected_value="0 months (on track)",
                    actual_value=f"{actual_schedule_slip} months delayed",
                    coherence_score=round(max(0, 1 - actual_schedule_slip / 24), 2),
                    severity="HIGH" if actual_schedule_slip > 6 else "MODERATE",
                    explanation=(
                        f"Narrative claims the project is on track, but schedule has "
                        f"slipped by {actual_schedule_slip:.0f} months from the baseline."
                    ),
                ))

        cost_match = re.search(r"₹(\d+(?:\.\d+)?)", claim)
        if cost_match and actual_cost is not None:
            claimed_cost = float(cost_match.group(1))
            diff_pct = abs(claimed_cost - actual_cost) / max(actual_cost, 1) * 100
            if diff_pct > 15:
                contradictions.append(NIDContradictionResult(
                    claim=claim,
                    referenced_cuf_field="revised_cost / expenditure",
                    expected_value=f"₹{claimed_cost} Cr (narrative)",
                    actual_value=f"₹{actual_cost:.2f} Cr (CUF)",
                    coherence_score=round(max(0, 1 - diff_pct / 100), 2),
                    severity="HIGH" if diff_pct > 30 else "MODERATE",
                    explanation=(
                        f"Narrative mentions ₹{claimed_cost} Cr, but CUF reports "
                        f"₹{actual_cost:.2f} Cr. Difference of {diff_pct:.1f}%."
                    ),
                ))

    return contradictions


def _compute_nqc(contradictions: list[NIDContradictionResult]) -> float:
    """Narrative-Quantitative Coherence score (0-100).

    100 = fully coherent, 0 = severe contradictions.
    """
    if not contradictions:
        return 95.0  # Minor deduction for rule-based limitations

    severity_weights = {"LOW": 5, "MODERATE": 15, "HIGH": 25, "CRITICAL": 40}
    total_deduction = sum(severity_weights.get(c.severity, 10) for c in contradictions)
    return round(max(0, 100 - total_deduction), 2)


def run_nid(
    *,
    narrative_text: str | None,
    actual_progress: float | None = None,
    actual_cost: float | None = None,
    actual_schedule_slip: float | None = None,
    use_llm: bool = False,
    ollama_base_url: str = "http://localhost:11434",
) -> NIDResult:
    """Run the Narrative Inconsistency Detector.

    Falls back to rule-based extraction if LLM is unavailable.
    """
    model_version = "demo_rule_based_v1"
    prompt_version = "v1"

    if not narrative_text or not narrative_text.strip():
        return NIDResult(
            status="unavailable",
            nqc_score=None,
            confidence=None,
            extracted_claims=[],
            contradictions=[],
            model_version=model_version,
            prompt_version=prompt_version,
            error_message="No narrative text available for NID analysis.",
        )

    # Attempt LLM-based extraction if enabled
    if use_llm:
        try:
            claims = _extract_claims_llm(narrative_text, ollama_base_url)
            model_version = "ollama_llama3_v1"
        except Exception as exc:
            logger.warning("Ollama NID extraction failed, falling back to rule-based: %s", exc)
            claims = _extract_claims_rule_based(narrative_text)
    else:
        claims = _extract_claims_rule_based(narrative_text)

    contradictions = _cross_check_claims(
        claims,
        actual_progress=actual_progress,
        actual_cost=actual_cost,
        actual_schedule_slip=actual_schedule_slip,
    )

    nqc = _compute_nqc(contradictions)
    confidence = "HIGH" if nqc >= 80 else ("MODERATE" if nqc >= 50 else "LOW")

    return NIDResult(
        status="available",
        nqc_score=nqc,
        confidence=confidence,
        extracted_claims=claims,
        contradictions=contradictions,
        model_version=model_version,
        prompt_version=prompt_version,
        error_message=None,
    )


def _extract_claims_llm(narrative: str, ollama_base_url: str) -> list[str]:
    """Attempt LLM-based claim extraction via Ollama.

    Raises on any failure so caller can fall back to rule-based.
    """
    import httpx

    prompt = (
        "Extract specific quantitative claims from this infrastructure project narrative. "
        "Return each claim on a separate line, prefixed with 'CLAIM: '. "
        "Focus on: progress percentages, cost figures, schedule statements, "
        "delay mentions, and quality assertions.\n\n"
        f"Narrative:\n{narrative}\n\n"
        "Claims:"
    )

    response = httpx.post(
        f"{ollama_base_url}/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False},
        timeout=30.0,
    )
    response.raise_for_status()

    text = response.json().get("response", "")
    claims = [
        line.replace("CLAIM:", "").strip()
        for line in text.split("\n")
        if line.strip().startswith("CLAIM:")
    ]

    if not claims:
        raise ValueError("LLM returned no extractable claims")

    return claims
