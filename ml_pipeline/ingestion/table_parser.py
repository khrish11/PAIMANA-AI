"""Parse PAIMANA flash report PDF tables into structured records.

Primary target: Table 6 (All Ongoing Projects) — 8-column per-project table
with ~1981 rows spanning ~107 pages per monthly report.

Secondary targets:
  - Table 1 (Ministry-wise Ongoing Projects) for ministry/sector mapping
  - Table 2 (State-wise Ongoing Projects) for state-level rollups
  - Table 3 (Completed Projects) for completed-project records
  - Table 4 (Newly Added Projects) for newly-added records
  - Overview summary statistics
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ProjectRecord:
    """One project row from Table 6 (All Ongoing Projects)."""

    sl_no: int
    project_name: str
    agency: str
    project_code: str
    legacy_ocms_code: Optional[str] = None
    pmgid: Optional[str] = None
    state: str = ""
    approval_date: Optional[str] = None  # MM/YYYY
    start_date: Optional[str] = None  # MM/YYYY (often same as approval)
    original_doc: Optional[str] = None  # target date of completion MM/YYYY
    revised_doc: Optional[str] = None  # revised date of completion MM/YYYY
    original_cost_crore: Optional[float] = None
    revised_cost_crore: Optional[float] = None
    cumulative_expenditure_crore: Optional[float] = None
    physical_progress_pct: Optional[float] = None
    sector: Optional[str] = None  # filled by normalize step
    ministry: Optional[str] = None  # filled by normalize step


@dataclass
class MinistrySectorMapping:
    """A row from Table 1 mapping ministry -> sector -> costs."""

    ministry: str
    sector: str
    project_count: int
    original_cost_crore: Optional[float] = None
    revised_cost_crore: Optional[float] = None
    cumulative_expenditure_crore: Optional[float] = None


@dataclass
class CompletedProjectRecord:
    """A row from Table 3 (Completed Projects)."""

    project_name: str
    agency: str
    state: str
    approval_date: Optional[str] = None
    actual_doc: Optional[str] = None
    revised_doc: Optional[str] = None
    original_cost_crore: Optional[float] = None
    revised_cost_crore: Optional[float] = None
    cumulative_expenditure_crore: Optional[float] = None


@dataclass
class NewProjectRecord:
    """A row from Table 4 (Newly Added Projects)."""

    project_name: str
    agency: str
    project_code: str
    state: str
    approval_date: Optional[str] = None
    original_cost_crore: Optional[float] = None
    revised_cost_crore: Optional[float] = None
    cumulative_expenditure_crore: Optional[float] = None


@dataclass
class OverviewStats:
    """Summary numbers from the report overview page."""

    total_ongoing: Optional[int] = None
    original_cost_crore: Optional[float] = None
    revised_cost_crore: Optional[float] = None
    cumulative_expenditure_crore: Optional[float] = None
    commissioned_this_month: Optional[int] = None
    newly_added_this_month: Optional[int] = None


@dataclass
class ParseResult:
    """Full parse result for one PDF."""

    source_file: str
    reporting_period: str  # YYYY-MM
    overview: Optional[OverviewStats] = None
    projects: list[ProjectRecord] = field(default_factory=list)
    ministry_sector_map: list[MinistrySectorMapping] = field(default_factory=list)
    completed_projects: list[CompletedProjectRecord] = field(default_factory=list)
    new_projects: list[NewProjectRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INR_CRORE_RE = re.compile(r"[₹\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")
_NEWLINE_RE = re.compile(r"\n")


def _clean_text(text: str | None) -> str:
    """Collapse whitespace, strip, normalise rupee symbols."""
    if text is None:
        return ""
    text = text.replace("\n", " ")
    text = _INR_CRORE_RE.sub("", text)
    return _MULTI_SPACE_RE.sub(" ", text).strip()


def _parse_crore(value: str | None) -> Optional[float]:
    """Parse an Indian-crore numeric string (may contain commas)."""
    if value is None:
        return None
    value = _clean_text(value)
    if not value or value in ("-", "NA", "N/A", ""):
        return None
    # Remove commas used as thousands separators
    value = value.replace(",", "")
    try:
        return float(value)
    except ValueError:
        return None


def _parse_pct(value: str | None) -> Optional[float]:
    if value is None:
        return None
    value = _clean_text(value)
    value = value.rstrip("%")
    if not value or value in ("-", "NA", "N/A"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_int(value: str | None) -> Optional[int]:
    if value is None:
        return None
    value = _clean_text(value).replace(",", "")
    if not value or value in ("-", "NA", "N/A"):
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _parse_project_cell(cell_text: str) -> dict:
    """Parse the multi-line Project Name cell.

    Format::

        Project Name
        (Agency)
        (ProjectCode)
        (Legacy OCMS Code) (PMGID)

    Returns dict with keys: project_name, agency, project_code,
    legacy_ocms_code, pmgid.
    """
    lines = [ln.strip() for ln in cell_text.split("\n") if ln.strip()]
    result: dict = {
        "project_name": "",
        "agency": "",
        "project_code": "",
        "legacy_ocms_code": None,
        "pmgid": None,
    }

    if not lines:
        return result

    # Identify parenthesised segments
    paren_lines: list[str] = []
    name_lines: list[str] = []

    for line in lines:
        # Check if entire line is parenthesised (possibly after stripping)
        stripped = line.strip()
        if stripped.startswith("(") and stripped.endswith(")"):
            paren_lines.append(stripped)
        elif stripped.startswith("("):
            # Might be split across lines — accumulate
            paren_lines.append(stripped)
        elif paren_lines and not paren_lines[-1].endswith(")"):
            # Continuation of previous paren segment
            paren_lines[-1] += " " + stripped
        else:
            name_lines.append(stripped)

    result["project_name"] = " ".join(name_lines) if name_lines else ""

    # Extract agency, project_code, etc. from paren segments
    agency_parts: list[str] = []
    for p in paren_lines:
        inner = p.strip("()")
        # Project code: pure numeric, 6 digits
        if re.match(r"^\d{5,7}$", inner):
            result["project_code"] = inner
        # Legacy OCMS: starts with N followed by digits, or just digits with dash
        elif re.match(r"^N\d{5,}$", inner) or inner == "-":
            result["legacy_ocms_code"] = inner
        # PMGID: 4-digit number
        elif re.match(r"^\(\d{3,5}\)$", inner) or re.match(r"^\d{3,5}$", inner):
            result["pmgid"] = inner.strip("()")
        elif inner == "-":
            # Could be either legacy_ocms or pmgid placeholder
            if result["legacy_ocms_code"] is None:
                result["legacy_ocms_code"] = "-"
            else:
                result["pmgid"] = "-"
        else:
            agency_parts.append(inner)

    result["agency"] = " ".join(agency_parts)
    return result


def _parse_date_cell(value: str | None) -> tuple[Optional[str], Optional[str]]:
    """Parse a date cell like '04/2017\\n(04/2017)' into (primary, revised).

    Format is MM/YYYY or (MM/YYYY) for revised.
    """
    if not value:
        return None, None
    value = _clean_text(value)
    # Pattern: MM/YYYY (MM/YYYY) or just MM/YYYY
    match = re.search(r"(\d{2}/\d{4})", value)
    primary = match.group(1) if match else None
    # Look for second date in parentheses
    revised_match = re.search(r"\((\d{2}/\d{4})\)", value)
    revised = revised_match.group(1) if revised_match else None
    # If no parenthesised date, check for second date after first
    if revised is None and primary:
        after = value[value.index(primary) + 7 :].strip()
        match2 = re.search(r"(\d{2}/\d{4})", after)
        if match2:
            revised = match2.group(1)
    return primary, revised


def _parse_cost_cell(value: str | None) -> tuple[Optional[float], Optional[float]]:
    """Parse cost cell like '21030\\n(21030)' into (original, revised).

    Or '1,054,523\\n1,081,116' without parens.
    """
    if not value:
        return None, None
    value = value.replace("\n", " ").strip()

    # Try parenthesised revised cost first
    revised_match = re.search(r"\(([^)]+)\)", value)
    revised = _parse_crore(revised_match.group(1)) if revised_match else None

    # Original cost: first number before any paren or second number
    # Remove parenthesised part to find original
    if revised_match:
        before_paren = value[: value.index(revised_match.group(0))].strip()
    else:
        before_paren = value

    # Split on whitespace — first number is original
    nums = re.findall(r"[\d,]+\.?\d*", before_paren)
    original = _parse_crore(nums[0]) if nums else None

    # If no paren and we found two numbers, second is revised
    if revised is None and len(nums) >= 2:
        revised = _parse_crore(nums[1])

    return original, revised


# ---------------------------------------------------------------------------
# Table 6 parser (All Ongoing Projects)
# ---------------------------------------------------------------------------

def _is_header_row(row: list[str]) -> bool:
    """Check if a row is a table header."""
    if not row:
        return False
    joined = " ".join(_clean_text(c) for c in row if c).lower()
    # Table 6 headers contain sl.no and project/physical
    # Sector overview headers contain sl.no and sector name/project count
    return "sl.no" in joined and ("project" in joined or "physical" in joined or "sector" in joined)


def _is_subtotal_row(row: list[str]) -> bool:
    """Check if row is a 'Total (N)' subtotal."""
    if not row:
        return False
    cell = _clean_text(row[1] if len(row) > 1 else "")
    return cell.startswith("Total (") or cell.startswith("Total(")


def _is_section_header(row: list[str]) -> bool:
    """Check if row is a ministry/sector section header (no sl_no)."""
    if not row:
        return False
    first = _clean_text(row[0])
    # Section headers have empty Sl.No
    return first == "" and len(row) > 1


def parse_table6_pages(
    pdf_path: Path,
    start_page: int = 50,
    end_page: int | None = None,
) -> tuple[list[ProjectRecord], list[str]]:
    """Extract Table 6 (All Ongoing Projects) from a PDF.

    Returns (projects, warnings).
    """
    projects: list[ProjectRecord] = []
    warnings: list[str] = []
    current_ministry = ""
    current_sector = ""

    if pdfplumber is None:
        raise ImportError("pdfplumber is required for PDF parsing")

    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        if end_page is None:
            end_page = len(pages)

        for page_idx in range(start_page, min(end_page, len(pages))):
            page = pages[page_idx]
            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                for row in table:
                    # Skip empty rows
                    if not row or all(c is None for c in row):
                        continue

                    # Ensure row has expected columns
                    if len(row) < 6:
                        continue

                    # Normalise row to at least 8 columns
                    while len(row) < 8:
                        row.append(None)

                    # Skip headers
                    if _is_header_row(row):
                        continue

                    # Handle section headers (ministry/sector)
                    if _is_section_header(row):
                        cell1 = _clean_text(row[1])
                        if cell1 and not cell1.startswith("Total"):
                            # Could be ministry or sector name
                            if not current_ministry:
                                current_ministry = cell1
                            else:
                                current_sector = cell1
                        continue

                    # Handle subtotal rows
                    if _is_subtotal_row(row):
                        continue

                    # Parse project row
                    sl_no_val = _parse_int(row[0])
                    if sl_no_val is None:
                        # Might be a continuation row or section header
                        cell1 = _clean_text(row[1]) if len(row) > 1 else ""
                        if cell1 and not cell1.startswith("Total"):
                            # Could be ministry/sector header
                            # Determine if it's a ministry or sector by checking
                            # if a later row in this block has sector-level data
                            if not current_ministry:
                                current_ministry = cell1
                            elif not current_sector:
                                current_sector = cell1
                            # If both set, this might be a new ministry block
                            elif "Ministry" in cell1 or "Department" in cell1:
                                current_ministry = cell1
                                current_sector = ""
                        continue

                    # Validate this looks like a project row (not a sector overview)
                    # Table 6 project rows have numeric state-check: state should be
                    # a state name, not a number (sector overviews have project count
                    # in the state position)
                    state_val = _clean_text(row[2])
                    if state_val and state_val.isdigit():
                        # This is a sector overview row, skip it
                        continue

                    # Parse project name cell
                    name_cell = row[1] if row[1] else ""
                    parsed_name = _parse_project_cell(name_cell)

                    state = _clean_text(row[2])

                    # Dates
                    approval_primary, approval_revised = _parse_date_cell(row[3])
                    doc_primary, doc_revised = _parse_date_cell(row[4])

                    # Costs
                    orig_cost, revised_cost = _parse_cost_cell(row[5])

                    # Expenditure and progress
                    expenditure = _parse_crore(row[6]) if len(row) > 6 else None
                    progress = _parse_pct(row[7]) if len(row) > 7 else None

                    proj = ProjectRecord(
                        sl_no=sl_no_val,
                        project_name=parsed_name["project_name"],
                        agency=parsed_name["agency"],
                        project_code=parsed_name["project_code"],
                        legacy_ocms_code=parsed_name["legacy_ocms_code"],
                        pmgid=parsed_name["pmgid"],
                        state=state,
                        approval_date=approval_primary,
                        start_date=approval_revised,
                        original_doc=doc_primary,
                        revised_doc=doc_revised,
                        original_cost_crore=orig_cost,
                        revised_cost_crore=revised_cost,
                        cumulative_expenditure_crore=expenditure,
                        physical_progress_pct=progress,
                        sector=current_sector or None,
                        ministry=current_ministry or None,
                    )
                    projects.append(proj)

                # After processing a table, reset section tracking for next table
                # (ministry/sector context resets per table block)

    return projects, warnings


# ---------------------------------------------------------------------------
# Table 1 parser (Ministry-wise Ongoing Projects)
# ---------------------------------------------------------------------------

def parse_table1(pdf_path: Path) -> tuple[list[MinistrySectorMapping], list[str]]:
    """Extract Table 1 (Ministry-wise) sector mapping."""
    mappings: list[MinistrySectorMapping] = []
    warnings: list[str] = []
    current_ministry = ""

    if pdfplumber is None:
        raise ImportError("pdfplumber is required for PDF parsing")

    with pdfplumber.open(pdf_path) as pdf:
        # Table 1 is typically on pages 23-24
        for page_idx in range(22, min(30, len(pdf.pages))):
            page = pdf.pages[page_idx]
            text = page.extract_text() or ""
            if "TABLE 1" not in text.upper() and "Ministry-wise" not in text:
                # Check if we're still in Table 1 context
                if not any(
                    "Ministry-wise" in (pdf.pages[i].extract_text() or "")
                    for i in range(max(0, page_idx - 2), page_idx)
                ):
                    continue

            tables = page.extract_tables()
            for table in tables:
                if len(table) < 2:
                    continue
                for row in table:
                    if not row or len(row) < 5:
                        continue

                    # Header row
                    joined = " ".join(_clean_text(c) for c in row if c).lower()
                    if "sl.no" in joined or "allocated" in joined:
                        continue

                    # Check for ministry header (col 1 has ministry, rest null)
                    col1 = _clean_text(row[1])
                    col2 = _clean_text(row[2]) if len(row) > 2 else ""
                    col3 = _clean_text(row[3]) if len(row) > 3 else ""

                    if col1 and not col2 and not col3:
                        # This is a ministry header row
                        current_ministry = col1
                        continue

                    # Data row: Sl.No, Allocated To (may be None), Sector, Count, Costs
                    sector = col2 if col2 else col1  # depending on alignment
                    count = _parse_int(row[3] if len(row) > 3 else None)
                    orig = _parse_crore(row[4].split("\\n")[0] if len(row) > 4 else None)
                    revised_line = row[4].split("\\n")[1] if len(row) > 4 and "\\n" in (row[4] or "") else None
                    revised = _parse_crore(revised_line)
                    expenditure = _parse_crore(row[5] if len(row) > 5 else None)

                    if count is not None and sector:
                        mappings.append(
                            MinistrySectorMapping(
                                ministry=current_ministry,
                                sector=sector,
                                project_count=count,
                                original_cost_crore=orig,
                                revised_cost_crore=revised,
                                cumulative_expenditure_crore=expenditure,
                            )
                        )

    return mappings, warnings


# ---------------------------------------------------------------------------
# Overview stats parser
# ---------------------------------------------------------------------------

def _parse_overview_from_text(text: str) -> Optional[OverviewStats]:
    """Extract overview statistics from the overview page text."""
    if not text:
        return None

    stats = OverviewStats()

    # Pattern: "1981 | 17 ₹ 37,12,662 ₹ 42,78,402 ₹ 20,36,107"
    # or similar: total_projects | new ₹ orig_cost ₹ rev_cost ₹ expenditure
    match = re.search(
        r"(\d[\d,]*)\s*\|\s*(\d+)\s*₹\s*([\d,]+)\s*₹\s*([\d,]+)\s*₹\s*([\d,]+)",
        text,
    )
    if match:
        stats.total_ongoing = _parse_int(match.group(1))
        stats.newly_added_this_month = _parse_int(match.group(2))
        stats.original_cost_crore = _parse_crore(match.group(3))
        stats.revised_cost_crore = _parse_crore(match.group(4))
        stats.cumulative_expenditure_crore = _parse_crore(match.group(5))

    # Commissioned: "9 55" pattern
    commissioned_match = re.search(r"(\d+)\s+(\d+)\s*\n", text)
    # Or look for "Commissioned during month" nearby
    comm_match = re.search(r"(\d+)\s+Commissioned during month", text)
    if comm_match:
        stats.commissioned_this_month = _parse_int(comm_match.group(1))

    if stats.total_ongoing is None:
        return None
    return stats


# ---------------------------------------------------------------------------
# Main extraction orchestrator
# ---------------------------------------------------------------------------

def _detect_table6_start(pdf_path: Path) -> int:
    """Find the page index where Table 6 data starts.

    The PDF has a title page ("Table 6: All Ongoing Projects") typically
    around page 54, followed by data pages with 8-column tables.  Earlier
    pages reference Table 6 in the TOC or have sector overview tables —
    we skip those by requiring the title to appear without the TOC markers
    (CONTENTS, "I.", "II.", etc.) and/or requiring 8-column tables.
    """
    if pdfplumber is None:
        raise ImportError("pdfplumber is required")

    with pdfplumber.open(pdf_path) as pdf:
        # Phase 1: find the explicit title page
        title_page_idx: int | None = None
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # Must have the exact title format, not just TOC reference
            if "Table 6" in text and "All Ongoing Projects" in text:
                # Exclude TOC pages (they have CONTENTS or section numbers)
                if "CONTENTS" in text.upper():
                    continue
                # The title page itself has the report period but no data
                title_page_idx = i
                break

        if title_page_idx is not None:
            # Data starts on the next page
            return title_page_idx + 1

        # Phase 2: fallback — find first page with "All Ongoing Projects"
        # header AND 8-column tables
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if "All Ongoing Projects" in text:
                tables = page.extract_tables()
                if tables:
                    for t in tables:
                        if t and len(t[0]) >= 8:
                            return i
    return 50  # fallback


def _detect_overview_page(pdf_path: Path) -> int:
    """Find the overview page (page 4 typically)."""
    if pdfplumber is None:
        raise ImportError("pdfplumber is required")

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[:10]):
            text = page.extract_text() or ""
            if "Ongoing Projects" in text and "|" in text and "₹" in text:
                return i
    return 3  # fallback


def _detect_table1_start(pdf_path: Path) -> int:
    """Find Table 1 start page."""
    if pdfplumber is None:
        raise ImportError("pdfplumber is required")

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if "TABLE 1" in text.upper() and "Ministry-wise" in text.upper():
                return i
    return 23  # fallback


def parse_flash_report(pdf_path: Path, reporting_period: str = "") -> ParseResult:
    """Parse a PAIMANA flash report PDF into structured records.

    Args:
        pdf_path: Path to the PDF file.
        reporting_period: String like '2026-04'. If empty, inferred from filename.

    Returns:
        ParseResult with all extracted records.
    """
    result = ParseResult(
        source_file=pdf_path.name,
        reporting_period=reporting_period,
    )

    if pdfplumber is None:
        result.warnings.append("pdfplumber not installed")
        return result

    # 1. Parse overview
    try:
        overview_page = _detect_overview_page(pdf_path)
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[overview_page].extract_text() or ""
        result.overview = _parse_overview_from_text(text)
    except Exception as e:
        result.warnings.append(f"Overview parse failed: {e}")

    # 2. Parse Table 6 (All Ongoing Projects) — the primary data
    try:
        table6_start = _detect_table6_start(pdf_path)
        with pdfplumber.open(pdf_path) as pdf:
            table6_end = len(pdf.pages)
        projects, proj_warnings = parse_table6_pages(pdf_path, table6_start, table6_end)
        result.projects = projects
        result.warnings.extend(proj_warnings)
    except Exception as e:
        result.warnings.append(f"Table 6 parse failed: {e}")

    # 3. Parse Table 1 (Ministry-wise) for sector mapping
    try:
        mappings, map_warnings = parse_table1(pdf_path)
        result.ministry_sector_map = mappings
        result.warnings.extend(map_warnings)
    except Exception as e:
        result.warnings.append(f"Table 1 parse failed: {e}")

    return result


def count_projects(pdf_path: Path) -> dict:
    """Quick scan to count projects and identify table boundaries.

    Returns dict with page_count, table6_pages, estimated_projects.
    """
    if pdfplumber is None:
        raise ImportError("pdfplumber is required")

    info = {"page_count": 0, "table6_pages": 0, "estimated_projects": 0}

    with pdfplumber.open(pdf_path) as pdf:
        info["page_count"] = len(pdf.pages)
        in_table6 = False

        for page in pdf.pages:
            text = page.extract_text() or ""
            if "All Ongoing Projects" in text:
                in_table6 = True
                info["table6_pages"] += 1
            elif in_table6 and "All Ongoing Projects" not in text:
                # Might have left Table 6
                pass  # Keep going, header might be on next page

            if in_table6:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row and row[0] and _parse_int(row[0]) is not None:
                            info["estimated_projects"] += 1

    return info
