#!/usr/bin/env python3
"""
Bug Bounty Knowledge Base & Data Indexing Manager.

Standard Library ONLY: json, pathlib, re, argparse, dataclasses, datetime, math, sys.
Python 3.14+ compatible.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

# ==============================================================================
# Constants & Enums
# ==============================================================================

ALLOWED_PLATFORMS = {
    "HackerOne",
    "Bugcrowd",
    "Intigriti",
    "Immunefi",
    "Direct/Private",
    "Other",
}

ALLOWED_TYPES = {
    "success",
    "failure",
    "target_profile",
    "investigation",
    "playbook",
    "report",
}

ALLOWED_STATUSES = {
    "Hunting",
    "In-Triage",
    "Rewarded",
    "Duplicate",
    "Informative",
    "Rejected",
    "Out-of-Scope",
}

RESOLVED_STATUSES = {
    "Rewarded",
    "Duplicate",
    "Informative",
    "Rejected",
    "Out-of-Scope",
}

ALLOWED_SEVERITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
    "None",
}

ALLOWED_ROOT_CAUSES = {
    "Access Control",
    "Business Logic",
    "Input Validation",
    "Authentication",
    "Configuration",
    "Race Condition",
    "Information Disclosure",
    "N/A",
}

ALLOWED_FAILURE_REASONS = {
    "Duplicate (Speed)",
    "Out of Scope",
    "By Design / Informative",
    "WAF / Mitigated",
    "Insufficient Impact",
}

TYPE_ID_PREFIX_MAPPING = {
    "success": {"KB"},
    "failure": {"KB"},
    "target_profile": {"TGT"},
    "investigation": {"INV"},
    "report": {"REP"},
    "playbook": {"PB"},
}

ID_REGEX = re.compile(r"^(KB|TGT|REP|INV|PB)-[A-Za-z0-9_-]+$")
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ==============================================================================
# Data Models
# ==============================================================================

@dataclass
class BountyRecord:
    id: str
    title: str
    target: str
    platform: str
    date: str
    type: str
    status: str
    severity: str
    cvss_score: float | None
    bounty_payout: float
    vuln_class: str
    root_cause_category: str
    failure_reason: str | None
    techniques: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    file_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


# ==============================================================================
# Frontmatter Parser (Standard Library YAML Subset)
# ==============================================================================

def strip_comment(text: str) -> str:
    """Strips trailing # comment only when # occurs outside quotes."""
    in_single = False
    in_double = False
    escape = False
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "'" and not in_double:
            in_single = not in_single
        elif ch == "#" and not in_single and not in_double:
            return text[:i].rstrip()
    return text.rstrip()


def split_inline_list(inner: str) -> list[str]:
    """Splits an inline list [a, b, c] on commas occurring outside quotes."""
    items: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    escape = False

    for ch in inner:
        if escape:
            current.append(ch)
            escape = False
            continue
        if ch == "\\":
            escape = True
            current.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
        elif ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
        elif ch == "," and not in_single and not in_double:
            token = "".join(current).strip()
            if token:
                items.append(token)
            current = []
        else:
            current.append(ch)

    last_token = "".join(current).strip()
    if last_token:
        items.append(last_token)

    cleaned_items: list[str] = []
    for token in items:
        clean = token.strip()
        if (clean.startswith('"') and clean.endswith('"')) or (
            clean.startswith("'") and clean.endswith("'")
        ):
            clean = clean[1:-1]
        if clean:
            cleaned_items.append(clean)
    return cleaned_items


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """
    Parses frontmatter delimited by opening and closing '---'.
    Returns (metadata_dict, body_markdown).
    """
    text = text.lstrip("\ufeff")
    pattern = re.compile(r"^\s*---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n(.*))?$", re.DOTALL)
    match = pattern.match(text)
    if not match:
        raise ValueError("Missing or invalid frontmatter delimiter (expected opening and closing '---')")

    raw_yaml = match.group(1)
    body = match.group(2) if match.group(2) is not None else ""

    metadata: dict[str, Any] = {}
    pending_list_key: str | None = None

    lines = raw_yaml.splitlines()
    for line in lines:
        stripped = line.strip()

        # Skip empty lines or full-line comments
        if not stripped or stripped.startswith("#"):
            continue

        # Handle list item continuation under multiline list
        if stripped.startswith("- "):
            item_val = stripped[2:].strip()
            item_val = strip_comment(item_val)
            if (item_val.startswith('"') and item_val.endswith('"')) or (
                item_val.startswith("'") and item_val.endswith("'")
            ):
                item_val = item_val[1:-1]
            if pending_list_key is not None:
                if pending_list_key not in metadata or not isinstance(metadata[pending_list_key], list):
                    metadata[pending_list_key] = []
                metadata[pending_list_key].append(item_val)
            continue

        # If a pending list key was waiting for items and a non-list item is met, resolve it as None
        if pending_list_key is not None:
            if pending_list_key not in metadata:
                metadata[pending_list_key] = None
            pending_list_key = None

        # Key-value pair parsing
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val_str = parts[1].strip()

            val_str = strip_comment(val_str)

            if not val_str:
                # Multiline list or empty field: mark pending
                pending_list_key = key
                continue

            # Inline List: [a, b, c]
            if val_str.startswith("[") and val_str.endswith("]"):
                inner = val_str[1:-1].strip()
                if not inner:
                    metadata[key] = []
                else:
                    metadata[key] = split_inline_list(inner)
                continue

            # Null / None
            if val_str.lower() in ("null", "none", "~"):
                metadata[key] = None
                continue

            # Boolean
            if val_str.lower() == "true":
                metadata[key] = True
                continue
            if val_str.lower() == "false":
                metadata[key] = False
                continue

            # Number (int or float)
            try:
                if "." in val_str:
                    metadata[key] = float(val_str)
                    continue
                metadata[key] = int(val_str)
                continue
            except ValueError:
                pass

            # String with quotes
            if (val_str.startswith('"') and val_str.endswith('"')) or (
                val_str.startswith("'") and val_str.endswith("'")
            ):
                metadata[key] = val_str[1:-1]
                continue

            # Plain string
            metadata[key] = val_str

    if pending_list_key is not None:
        if pending_list_key not in metadata:
            metadata[pending_list_key] = None

    return metadata, body


# ==============================================================================
# Validation Engine
# ==============================================================================

def validate_record_metadata(meta: dict[str, Any], file_path: Path | str) -> tuple[bool, list[str]]:
    """
    Validates a dictionary of metadata against data-indexing-standard.md.
    Returns (is_valid, list_of_error_messages).
    """
    errors: list[str] = []

    # Required fields check
    required_fields = [
        "id",
        "title",
        "target",
        "platform",
        "date",
        "type",
        "status",
        "severity",
        "cvss_score",
        "bounty_payout",
        "vuln_class",
        "root_cause_category",
        "failure_reason",
        "techniques",
        "lessons_learned",
    ]

    for req in required_fields:
        if req not in meta:
            errors.append(f"Missing required frontmatter field: '{req}'")

    if errors:
        return False, errors

    # Field validations
    rec_id = str(meta.get("id", ""))
    if not ID_REGEX.match(rec_id):
        errors.append(f"Invalid id format '{rec_id}'. Must match pattern: ^(KB|TGT|REP|INV|PB)-[A-Za-z0-9_-]+$")

    raw_title = meta.get("title")
    if not isinstance(raw_title, str):
        errors.append("Field 'title' must be a string.")
    else:
        if "\n" in raw_title or "\r" in raw_title:
            errors.append("Field 'title' must be a single line without newlines.")
        title = raw_title.strip()
        if len(title) < 5 or len(title) > 140:
            errors.append(f"Field 'title' must be between 5 and 140 characters long (got {len(title)}).")

    target = str(meta.get("target", "")).strip()
    if not target:
        errors.append("Field 'target' cannot be empty.")

    platform = str(meta.get("platform", ""))
    if platform not in ALLOWED_PLATFORMS:
        errors.append(f"Invalid platform '{platform}'. Allowed: {sorted(ALLOWED_PLATFORMS)}")

    date_str = str(meta.get("date", ""))
    if not DATE_REGEX.match(date_str):
        errors.append(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"Date '{date_str}' is not a valid calendar date.")

    doc_type = str(meta.get("type", ""))
    if doc_type not in ALLOWED_TYPES:
        errors.append(f"Invalid type '{doc_type}'. Allowed: {sorted(ALLOWED_TYPES)}")

    # Check ID prefix matches document type
    if doc_type in TYPE_ID_PREFIX_MAPPING and "-" in rec_id:
        prefix = rec_id.split("-", 1)[0]
        allowed_prefixes = TYPE_ID_PREFIX_MAPPING[doc_type]
        if prefix not in allowed_prefixes:
            errors.append(
                f"ID prefix '{prefix}' does not match document type '{doc_type}' (expected one of {sorted(allowed_prefixes)})."
            )

    status = str(meta.get("status", ""))
    if status not in ALLOWED_STATUSES:
        errors.append(f"Invalid status '{status}'. Allowed: {sorted(ALLOWED_STATUSES)}")

    severity = str(meta.get("severity", ""))
    if severity not in ALLOWED_SEVERITIES:
        errors.append(f"Invalid severity '{severity}'. Allowed: {sorted(ALLOWED_SEVERITIES)}")

    cvss = meta.get("cvss_score")
    if cvss is not None:
        try:
            cvss_val = float(cvss)
            if not math.isfinite(cvss_val):
                errors.append(f"cvss_score '{cvss}' must be a finite numeric value.")
            elif not (0.0 <= cvss_val <= 10.0):
                errors.append(f"cvss_score '{cvss_val}' out of bounds (must be between 0.0 and 10.0).")
        except (ValueError, TypeError):
            errors.append(f"cvss_score '{cvss}' must be a float or null.")

    payout = meta.get("bounty_payout")
    payout_valid = False
    payout_val = 0.0
    try:
        payout_val = float(payout)
        if not math.isfinite(payout_val):
            errors.append(f"bounty_payout '{payout}' must be a finite numeric value.")
        elif payout_val < 0:
            errors.append(f"bounty_payout '{payout_val}' cannot be negative.")
        else:
            payout_valid = True
    except (ValueError, TypeError):
        errors.append(f"bounty_payout '{payout}' must be a numeric value >= 0.")

    if payout_valid:
        if status == "Rewarded" and payout_val <= 0.0:
            errors.append(
                f"Record with status 'Rewarded' must have a bounty_payout greater than 0 (got {payout_val})."
            )
        unrewarded_statuses = {
            "Duplicate",
            "Rejected",
            "Out-of-Scope",
            "Informative",
            "Hunting",
            "In-Triage",
        }
        if status in unrewarded_statuses and payout_val != 0.0:
            errors.append(
                f"Record with status '{status}' must have a bounty_payout of 0 (got {payout_val})."
            )

    vuln_class = str(meta.get("vuln_class", "")).strip()
    if not vuln_class:
        errors.append("Field 'vuln_class' cannot be empty.")

    root_cause = str(meta.get("root_cause_category", ""))
    if root_cause not in ALLOWED_ROOT_CAUSES:
        errors.append(f"Invalid root_cause_category '{root_cause}'. Allowed: {sorted(ALLOWED_ROOT_CAUSES)}")

    failure_reason = meta.get("failure_reason")
    if failure_reason is not None:
        if not isinstance(failure_reason, str) or failure_reason not in ALLOWED_FAILURE_REASONS:
            errors.append(f"Invalid failure_reason '{failure_reason}'. Allowed: {sorted(ALLOWED_FAILURE_REASONS)} or null")

    # Conditional Rule 1: failure type or failure status requires non-null failure_reason
    failure_statuses = {"Duplicate", "Rejected", "Out-of-Scope", "Informative"}
    if doc_type == "failure" or status in failure_statuses:
        if not failure_reason:
            errors.append(
                f"failure_reason must be specified when type='{doc_type}' or status='{status}'."
            )

    # Invariant: Rewarded status cannot have failure_reason
    if status == "Rewarded" and failure_reason is not None:
        errors.append(
            f"Record with status 'Rewarded' cannot have a failure_reason (got '{failure_reason}')."
        )

    # Techniques list
    techniques = meta.get("techniques")
    if not isinstance(techniques, list) or len(techniques) == 0:
        errors.append("Field 'techniques' must be a non-empty list of tags.")
    elif not all(isinstance(t, str) and t.strip() for t in techniques):
        errors.append("Field 'techniques' must contain only non-empty strings.")

    # Lessons learned list
    lessons = meta.get("lessons_learned")
    if not isinstance(lessons, list) or len(lessons) == 0:
        errors.append("Field 'lessons_learned' must be a non-empty list of bullet takeaways.")
    elif not all(isinstance(l, str) and l.strip() for l in lessons):
        errors.append("Field 'lessons_learned' must contain only non-empty strings.")

    return (len(errors) == 0), errors


# ==============================================================================
# Repository Scanner & Record Loader
# ==============================================================================

def find_markdown_files(repo_root: Path) -> list[Path]:
    """
    Discovers all indexable markdown files in knowledge-base/, targets/, investigations/, reports/.
    """
    search_dirs = ["knowledge-base", "targets", "investigations", "reports"]
    matched_files: list[Path] = []
    ignored_names = {"INDEX.md", "README.md"}

    for dir_name in search_dirs:
        target_dir = repo_root / dir_name
        if not target_dir.exists():
            continue
        for md_file in target_dir.rglob("*.md"):
            if md_file.name in ignored_names:
                continue
            matched_files.append(md_file)

    return sorted(matched_files)


def load_record_from_file(file_path: Path, repo_root: Path) -> tuple[BountyRecord | None, list[str]]:
    """
    Reads a markdown file, parses frontmatter, validates metadata, and builds BountyRecord.
    """
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except Exception as e:
        return None, [f"Could not read file: {e}"]

    try:
        meta, _ = parse_frontmatter(content)
    except Exception as e:
        return None, [f"Frontmatter parse error: {e}"]

    is_valid, errors = validate_record_metadata(meta, file_path)
    if not is_valid:
        return None, errors

    try:
        rel_path = file_path.relative_to(repo_root).as_posix()
    except ValueError:
        rel_path = file_path.as_posix()

    record = BountyRecord(
        id=str(meta["id"]),
        title=str(meta["title"]),
        target=str(meta["target"]),
        platform=str(meta["platform"]),
        date=str(meta["date"]),
        type=str(meta["type"]),
        status=str(meta["status"]),
        severity=str(meta["severity"]),
        cvss_score=float(meta["cvss_score"]) if meta.get("cvss_score") is not None else None,
        bounty_payout=float(meta["bounty_payout"]),
        vuln_class=str(meta["vuln_class"]),
        root_cause_category=str(meta["root_cause_category"]),
        failure_reason=str(meta["failure_reason"]) if meta.get("failure_reason") is not None else None,
        techniques=list(meta.get("techniques", [])),
        lessons_learned=list(meta.get("lessons_learned", [])),
        file_path=rel_path,
    )

    return record, []


# ==============================================================================
# Analytics & Statistics Engine
# ==============================================================================

def compute_statistics(records: list[BountyRecord]) -> dict[str, Any]:
    """
    Calculates summary metrics, win rate, duplicate rate, and multidimensional breakdowns.
    """
    total_earnings = sum(r.bounty_payout for r in records)
    total_records = len(records)

    resolved_records = [r for r in records if r.status in RESOLVED_STATUSES]
    total_resolved = len(resolved_records)
    rewarded_records = [r for r in records if r.status == "Rewarded"]
    duplicate_records = [r for r in records if r.status == "Duplicate"]

    win_rate = (len(rewarded_records) / total_resolved * 100.0) if total_resolved > 0 else 0.0
    duplicate_rate = (len(duplicate_records) / total_resolved * 100.0) if total_resolved > 0 else 0.0
    avg_payout = (total_earnings / len(rewarded_records)) if rewarded_records else 0.0

    counts_by_type: dict[str, int] = {}
    counts_by_status: dict[str, int] = {}
    counts_by_platform: dict[str, int] = {}
    bounty_by_platform: dict[str, float] = {}
    counts_by_severity: dict[str, int] = {}
    counts_by_vuln_class: dict[str, int] = {}
    bounty_by_vuln_class: dict[str, float] = {}
    counts_by_root_cause: dict[str, int] = {}
    techniques_freq: dict[str, int] = {}

    for r in records:
        counts_by_type[r.type] = counts_by_type.get(r.type, 0) + 1
        counts_by_status[r.status] = counts_by_status.get(r.status, 0) + 1
        counts_by_platform[r.platform] = counts_by_platform.get(r.platform, 0) + 1
        bounty_by_platform[r.platform] = bounty_by_platform.get(r.platform, 0.0) + r.bounty_payout
        counts_by_severity[r.severity] = counts_by_severity.get(r.severity, 0) + 1
        counts_by_vuln_class[r.vuln_class] = counts_by_vuln_class.get(r.vuln_class, 0) + 1
        bounty_by_vuln_class[r.vuln_class] = bounty_by_vuln_class.get(r.vuln_class, 0.0) + r.bounty_payout
        counts_by_root_cause[r.root_cause_category] = counts_by_root_cause.get(r.root_cause_category, 0) + 1

        for tech in r.techniques:
            techniques_freq[tech] = techniques_freq.get(tech, 0) + 1

    return {
        "total_earnings_usd": round(total_earnings, 2),
        "total_records": total_records,
        "total_resolved": total_resolved,
        "total_rewarded": len(rewarded_records),
        "total_duplicates": len(duplicate_records),
        "win_rate_percent": round(win_rate, 2),
        "duplicate_rate_percent": round(duplicate_rate, 2),
        "average_reward_usd": round(avg_payout, 2),
        "counts_by_type": dict(sorted(counts_by_type.items())),
        "counts_by_status": dict(sorted(counts_by_status.items())),
        "counts_by_platform": dict(sorted(counts_by_platform.items())),
        "bounty_by_platform": {k: round(v, 2) for k, v in sorted(bounty_by_platform.items())},
        "counts_by_severity": dict(sorted(counts_by_severity.items())),
        "counts_by_vuln_class": dict(sorted(counts_by_vuln_class.items())),
        "bounty_by_vuln_class": {k: round(v, 2) for k, v in sorted(bounty_by_vuln_class.items())},
        "counts_by_root_cause": dict(sorted(counts_by_root_cause.items())),
        "top_techniques": dict(sorted(techniques_freq.items(), key=lambda x: x[1], reverse=True)[:10]),
    }


# ==============================================================================
# Index Generator (JSON & Markdown)
# ==============================================================================

def generate_index_markdown(records: list[BountyRecord], stats: dict[str, Any]) -> str:
    """
    Generates human-readable INDEX.md with summary cards, analytics tables, and record inventory.
    """
    lines = [
        "# Bug Bounty Knowledge Base Index & Analytics",
        f"*Auto-compiled on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*",
        "",
        "## Executive Performance Summary",
        "",
        f"- **Total Payout Earnings:** `${stats['total_earnings_usd']:,.2f}`",
        f"- **Win Rate (Rewarded / Resolved):** `{stats['win_rate_percent']}%` ({stats['total_rewarded']}/{stats['total_resolved']})",
        f"- **Duplicate Rate:** `{stats['duplicate_rate_percent']}%` ({stats['total_duplicates']}/{stats['total_resolved']})",
        f"- **Average Bounty per Rewarded Bug:** `${stats['average_reward_usd']:,.2f}`",
        f"- **Total Tracked Records:** `{stats['total_records']}`",
        "",
        "---",
        "",
        "## Platform Breakdown",
        "",
        "| Platform | Findings | Total Bounty ($) | Avg Bounty ($) |",
        "| :--- | :---: | :---: | :---: |",
    ]

    for plat, count in stats["counts_by_platform"].items():
        bounty = stats["bounty_by_platform"].get(plat, 0.0)
        avg = (bounty / count) if count > 0 else 0.0
        safe_plat = plat.replace("|", r"\|")
        lines.append(f"| {safe_plat} | {count} | ${bounty:,.2f} | ${avg:,.2f} |")

    lines.extend([
        "",
        "## Vulnerability Class Breakdown",
        "",
        "| Vulnerability Class | Count | Total Bounty ($) |",
        "| :--- | :---: | :---: |",
    ])

    for vc, count in stats["counts_by_vuln_class"].items():
        bounty = stats["bounty_by_vuln_class"].get(vc, 0.0)
        safe_vc = vc.replace("|", r"\|")
        lines.append(f"| {safe_vc} | {count} | ${bounty:,.2f} |")

    lines.extend([
        "",
        "## Status Distribution",
        "",
        "| Status | Count |",
        "| :--- | :---: |",
    ])
    for st, count in stats["counts_by_status"].items():
        safe_st = st.replace("|", r"\|")
        lines.append(f"| {safe_st} | {count} |")

    lines.extend([
        "",
        "---",
        "",
        "## Complete Knowledge Base Inventory",
        "",
        "| ID | Title | Target | Platform | Type | Status | Severity | CVSS | Bounty ($) | Vuln Class | Path |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |",
    ])

    # Sort records: Rewarded first, then descending date
    sorted_records = sorted(
        records,
        key=lambda r: (0 if r.status == "Rewarded" else 1, r.date),
        reverse=False,
    )

    for r in sorted_records:
        cvss_str = f"{r.cvss_score:.1f}" if r.cvss_score is not None else "-"
        bounty_str = f"${r.bounty_payout:,.0f}" if r.bounty_payout > 0 else "$0"
        rel_link = f"[{r.file_path}](../{r.file_path})"
        safe_title = r.title.replace("|", r"\|")
        safe_target = r.target.replace("|", r"\|")
        safe_platform = r.platform.replace("|", r"\|")
        safe_vuln = r.vuln_class.replace("|", r"\|")
        lines.append(
            f"| `{r.id}` | {safe_title} | {safe_target} | {safe_platform} | `{r.type}` | `{r.status}` | {r.severity} | {cvss_str} | {bounty_str} | {safe_vuln} | {rel_link} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Tactical Lessons Learned Archive",
        "",
    ])

    for r in sorted_records:
        if r.lessons_learned:
            lines.append(f"### `{r.id}` - {r.title} ({r.target})")
            for lesson in r.lessons_learned:
                lines.append(f"- {lesson}")
            lines.append("")

    return "\n".join(lines)


# ==============================================================================
# CLI Commands Implementations
# ==============================================================================

def cmd_validate(repo_root: Path, target_path: Path | None = None) -> int:
    """
    Validates all or specific markdown files against schema.
    Returns 0 on success, 1 on validation error.
    """
    if target_path:
        files = [target_path] if target_path.is_file() else list(target_path.rglob("*.md"))
    else:
        files = find_markdown_files(repo_root)

    print(f"[*] Validating {len(files)} markdown file(s)...")
    passed = 0
    failed = 0

    for f in files:
        rec, errors = load_record_from_file(f, repo_root)
        rel_f = f.relative_to(repo_root).as_posix() if f.is_relative_to(repo_root) else f.as_posix()
        if errors:
            failed += 1
            print(f"[FAIL] {rel_f}:")
            for err in errors:
                print(f"       - {err}")
        else:
            passed += 1
            print(f"[PASS] {rel_f} (ID: {rec.id if rec else 'UNKNOWN'})")

    print(f"\n[+] Validation Summary: {passed} passed, {failed} failed out of {len(files)} file(s).")
    return 0 if failed == 0 else 1


def cmd_stats(repo_root: Path) -> int:
    """
    Prints aggregated statistics and KPIs to stdout.
    """
    files = find_markdown_files(repo_root)
    records: list[BountyRecord] = []
    errors_encountered = 0

    for f in files:
        rec, errs = load_record_from_file(f, repo_root)
        if rec:
            records.append(rec)
        else:
            errors_encountered += 1

    stats = compute_statistics(records)

    print("\n=======================================================")
    print("        BUG BOUNTY KNOWLEDGE BASE ANALYTICS            ")
    print("=======================================================")
    print(f"Total Earnings:            ${stats['total_earnings_usd']:,.2f}")
    print(f"Total Indexed Records:     {stats['total_records']}")
    print(f"Resolved Submissions:      {stats['total_resolved']}")
    print(f"Rewarded Submissions:      {stats['total_rewarded']}")
    print(f"Duplicate Submissions:     {stats['total_duplicates']}")
    print(f"Win Rate:                  {stats['win_rate_percent']}%")
    print(f"Duplicate Rate:            {stats['duplicate_rate_percent']}%")
    print(f"Average Payout:            ${stats['average_reward_usd']:,.2f}")
    print("-------------------------------------------------------")
    print("Breakdown by Platform:")
    for plat, count in stats["counts_by_platform"].items():
        bounty = stats["bounty_by_platform"].get(plat, 0.0)
        print(f"  - {plat:15}: {count:2} records | ${bounty:,.2f}")
    print("-------------------------------------------------------")
    print("Breakdown by Vulnerability Class:")
    for vc, count in stats["counts_by_vuln_class"].items():
        bounty = stats["bounty_by_vuln_class"].get(vc, 0.0)
        print(f"  - {vc:28}: {count:2} records | ${bounty:,.2f}")
    print("-------------------------------------------------------")
    print("Breakdown by Status:")
    for st, count in stats["counts_by_status"].items():
        print(f"  - {st:15}: {count:2}")
    print("-------------------------------------------------------")
    print("Top Offensive Techniques:")
    for tech, count in stats["top_techniques"].items():
        print(f"  - {tech:28}: {count}")
    print("=======================================================\n")

    if errors_encountered > 0:
        print(f"[!] Warning: {errors_encountered} file(s) failed validation and were excluded from stats.")

    return 0


def cmd_reindex(repo_root: Path) -> int:
    """
    Validates, computes stats, and compiles INDEX.json & INDEX.md.
    """
    print("[*] Initiating full repository reindexing...")
    files = find_markdown_files(repo_root)

    records: list[BountyRecord] = []
    errors_found = False

    for f in files:
        rec, errs = load_record_from_file(f, repo_root)
        rel_f = f.relative_to(repo_root).as_posix() if f.is_relative_to(repo_root) else f.as_posix()
        if errs:
            print(f"[!] Warning in {rel_f}: {', '.join(errs)}")
            errors_found = True
        elif rec:
            records.append(rec)

    stats = compute_statistics(records)

    # Compile INDEX.json
    kb_dir = repo_root / "knowledge-base"
    kb_dir.mkdir(parents=True, exist_ok=True)

    index_json_path = kb_dir / "INDEX.json"
    index_md_path = kb_dir / "INDEX.md"

    index_data = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(records),
        "metrics": stats,
        "records": [r.to_dict() for r in records],
    }

    index_json_path.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
    print(f"[+] Successfully wrote compiled index JSON -> {index_json_path.relative_to(repo_root)}")

    # Compile INDEX.md
    markdown_content = generate_index_markdown(records, stats)
    index_md_path.write_text(markdown_content, encoding="utf-8")
    print(f"[+] Successfully wrote compiled index Markdown -> {index_md_path.relative_to(repo_root)}")

    print(f"[+] Reindex complete! Processed {len(records)} valid records.")
    return 1 if errors_found else 0


def cmd_new(
    repo_root: Path,
    doc_type: str,
    record_id: str,
    title: str | None = None,
    target: str | None = None,
    platform: str | None = None,
    force: bool = False,
) -> int:
    """
    Generates a new markdown document from standard templates.
    """
    if not ID_REGEX.match(record_id):
        print(f"[ERROR] Invalid record_id '{record_id}'. Must match pattern: {ID_REGEX.pattern}")
        return 1

    type_mapping = {
        "target_profile": ("templates/target_profile.md", f"targets/{record_id}.md"),
        "target": ("templates/target_profile.md", f"targets/{record_id}.md"),
        "investigation": ("templates/investigation_record.md", f"investigations/{record_id}.md"),
        "bounty_report": ("templates/bounty_report.md", f"reports/{record_id}.md"),
        "report": ("templates/bounty_report.md", f"reports/{record_id}.md"),
        "success": ("templates/post_mortem_success.md", f"knowledge-base/successes/{record_id}.md"),
        "post_mortem_success": ("templates/post_mortem_success.md", f"knowledge-base/successes/{record_id}.md"),
        "failure": ("templates/post_mortem_failure.md", f"knowledge-base/failures/{record_id}.md"),
        "post_mortem_failure": ("templates/post_mortem_failure.md", f"knowledge-base/failures/{record_id}.md"),
        "playbook": ("templates/playbook.md", f"knowledge-base/vuln-playbooks/{record_id}.md"),
    }

    normalized_type = doc_type.lower()
    if normalized_type not in type_mapping:
        print(f"[ERROR] Unknown type '{doc_type}'. Allowed: {sorted(set(type_mapping.keys()))}")
        return 1

    template_rel, dest_rel = type_mapping[normalized_type]
    template_path = (repo_root / template_rel).resolve()
    dest_path = (repo_root / dest_rel).resolve()
    resolved_root = repo_root.resolve()

    try:
        if not dest_path.is_relative_to(resolved_root):
            print(f"[ERROR] Path traversal detected: destination '{dest_path}' is outside repository root.")
            return 1
    except (ValueError, AttributeError):
        print(f"[ERROR] Path traversal detected: destination '{dest_path}' is outside repository root.")
        return 1

    if not template_path.exists():
        print(f"[ERROR] Template file does not exist: {template_path}")
        return 1

    if dest_path.exists() and not force:
        print(f"[ERROR] Destination file already exists: {dest_path}. Use --force to overwrite.")
        return 1

    template_content = template_path.read_text(encoding="utf-8")

    # Substitutions
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    year_str = now.strftime("%Y")

    sub_title = title or f"Finding {record_id}"
    sub_target = target or "Target Organization"
    sub_platform = platform or "HackerOne"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", sub_target.lower()).strip("-")
    domain = f"{slug}.com"

    rendered = (
        template_content.replace("{{ID}}", record_id)
        .replace("{{TITLE}}", sub_title)
        .replace("{{TARGET}}", sub_target)
        .replace("{{PLATFORM}}", sub_platform)
        .replace("{{DATE}}", today_str)
        .replace("{{YEAR}}", year_str)
        .replace("{{TARGET_SLUG}}", slug)
        .replace("{{TARGET_DOMAIN}}", domain)
    )

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(rendered, encoding="utf-8")
    print(f"[+] Successfully scaffolded new {normalized_type} record at {dest_rel}")
    return 0


# ==============================================================================
# Main CLI Entry Point
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bug Bounty Knowledge Base & Data Indexing Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: reindex
    subparsers.add_parser("reindex", help="Scan repository, validate metadata, compile INDEX.json and INDEX.md")

    # Command: stats
    subparsers.add_parser("stats", help="Compute earnings, win rate, duplicate rate and breakdowns")

    # Command: validate
    val_parser = subparsers.add_parser("validate", help="Validate frontmatter against schema")
    val_parser.add_argument("--path", type=str, default=None, help="Specific file or directory to validate")

    # Command: new
    new_parser = subparsers.add_parser("new", help="Scaffold a new markdown record from templates")
    new_parser.add_argument("type", type=str, help="Record type (success, failure, target_profile, investigation, report, playbook)")
    new_parser.add_argument("id", type=str, help="Unique identifier (e.g. KB-2026-003, TGT-NEW-01)")
    new_parser.add_argument("--title", type=str, default=None, help="Descriptive title")
    new_parser.add_argument("--target", type=str, default=None, help="Target program name")
    new_parser.add_argument("--platform", type=str, default=None, help="Bug bounty platform")
    new_parser.add_argument("--force", action="store_true", help="Overwrite existing destination file")

    args = parser.parse_args()

    # Determine repo root (assuming script is located in scripts/)
    repo_root = Path(__file__).resolve().parent.parent

    if args.command == "reindex":
        exit_code = cmd_reindex(repo_root)
        sys.exit(exit_code)
    elif args.command == "stats":
        exit_code = cmd_stats(repo_root)
        sys.exit(exit_code)
    elif args.command == "validate":
        target = Path(args.path).resolve() if args.path else None
        exit_code = cmd_validate(repo_root, target)
        sys.exit(exit_code)
    elif args.command == "new":
        exit_code = cmd_new(
            repo_root=repo_root,
            doc_type=args.type,
            record_id=args.id,
            title=args.title,
            target=args.target,
            platform=args.platform,
            force=args.force,
        )
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
