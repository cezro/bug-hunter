#!/usr/bin/env python3
"""
Unit test suite for Bug Bounty Knowledge Base & Data Indexing Manager.
Runs via standard library unittest.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.index_manager import (
    BountyRecord,
    cmd_new,
    cmd_reindex,
    cmd_stats,
    cmd_validate,
    compute_statistics,
    generate_index_markdown,
    load_record_from_file,
    parse_frontmatter,
    validate_record_metadata,
)


class TestFrontmatterParser(unittest.TestCase):
    """Tests parsing YAML frontmatter without external dependencies."""

    def test_parse_valid_frontmatter(self):
        sample = """---
id: KB-2026-999
title: "Test Vulnerability Title"
target: Acme Corp
platform: HackerOne
date: 2026-05-01
type: success
status: Rewarded
severity: High
cvss_score: 8.5
bounty_payout: 2500
vuln_class: "CWE-639: IDOR"
root_cause_category: Access Control
failure_reason: null
techniques:
  - parameter-tampering
  - uuid-enumeration
lessons_learned:
  - "Takeaway one"
  - "Takeaway two"
---
# Document Body
Content goes here.
"""
        meta, body = parse_frontmatter(sample)
        self.assertEqual(meta["id"], "KB-2026-999")
        self.assertEqual(meta["title"], "Test Vulnerability Title")
        self.assertEqual(meta["target"], "Acme Corp")
        self.assertEqual(meta["platform"], "HackerOne")
        self.assertEqual(meta["date"], "2026-05-01")
        self.assertEqual(meta["type"], "success")
        self.assertEqual(meta["status"], "Rewarded")
        self.assertEqual(meta["severity"], "High")
        self.assertEqual(meta["cvss_score"], 8.5)
        self.assertEqual(meta["bounty_payout"], 2500)
        self.assertEqual(meta["vuln_class"], "CWE-639: IDOR")
        self.assertEqual(meta["root_cause_category"], "Access Control")
        self.assertIsNone(meta["failure_reason"])
        self.assertEqual(meta["techniques"], ["parameter-tampering", "uuid-enumeration"])
        self.assertEqual(meta["lessons_learned"], ["Takeaway one", "Takeaway two"])
        self.assertIn("# Document Body", body)

    def test_parse_inline_lists_and_booleans(self):
        sample = """---
id: TGT-TEST-01
title: Inline Test
target: Target
platform: Other
date: 2026-01-01
type: target_profile
status: Hunting
severity: None
cvss_score: null
bounty_payout: 0
vuln_class: N/A
root_cause_category: N/A
failure_reason: null
techniques: [recon, nmap, dirsearch]
lessons_learned: ["lesson A", "lesson B"]
is_active: true
is_deprecated: false
---
Body
"""
        meta, _ = parse_frontmatter(sample)
        self.assertEqual(meta["techniques"], ["recon", "nmap", "dirsearch"])
        self.assertEqual(meta["lessons_learned"], ["lesson A", "lesson B"])
        self.assertIs(meta["is_active"], True)
        self.assertIs(meta["is_deprecated"], False)

    def test_missing_opening_delimiter(self):
        sample = """id: KB-1
---
Body
"""
        with self.assertRaises(ValueError):
            parse_frontmatter(sample)

    def test_missing_closing_delimiter(self):
        sample = """---
id: KB-1
title: Test
"""
        with self.assertRaises(ValueError):
            parse_frontmatter(sample)


class TestValidationEngine(unittest.TestCase):
    """Tests strict metadata validation against data-indexing-standard.md."""

    def setUp(self):
        self.valid_meta = {
            "id": "KB-2026-101",
            "title": "Valid Sample Finding",
            "target": "ShopSecure",
            "platform": "HackerOne",
            "date": "2026-06-15",
            "type": "success",
            "status": "Rewarded",
            "severity": "Critical",
            "cvss_score": 9.8,
            "bounty_payout": 5000,
            "vuln_class": "CWE-287: Auth Bypass",
            "root_cause_category": "Authentication",
            "failure_reason": None,
            "techniques": ["jwt-forgery", "key-confusion"],
            "lessons_learned": ["Always verify JWT algorithm in server backend."],
        }

    def test_valid_metadata_passes(self):
        is_valid, errors = validate_record_metadata(self.valid_meta, "test.md")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_required_fields(self):
        meta = self.valid_meta.copy()
        del meta["platform"]
        del meta["cvss_score"]
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("platform" in e for e in errors))
        self.assertTrue(any("cvss_score" in e for e in errors))

    def test_invalid_id_format(self):
        meta = self.valid_meta.copy()
        meta["id"] = "INVALID_ID_FORMAT"
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid id format" in e for e in errors))

    def test_invalid_platform(self):
        meta = self.valid_meta.copy()
        meta["platform"] = "NonExistentPlatform"
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid platform" in e for e in errors))

    def test_invalid_date(self):
        meta = self.valid_meta.copy()
        meta["date"] = "2026-02-31"  # Invalid calendar date
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("not a valid calendar date" in e for e in errors))

    def test_cvss_score_out_of_bounds(self):
        meta = self.valid_meta.copy()
        meta["cvss_score"] = 10.5
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("cvss_score" in e for e in errors))

    def test_negative_bounty_payout(self):
        meta = self.valid_meta.copy()
        meta["bounty_payout"] = -100
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("cannot be negative" in e for e in errors))

    def test_failure_type_requires_failure_reason(self):
        meta = self.valid_meta.copy()
        meta["type"] = "failure"
        meta["status"] = "Duplicate"
        meta["bounty_payout"] = 0
        meta["failure_reason"] = None
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("failure_reason must be specified" in e for e in errors))

        # Adding valid failure reason should pass
        meta["failure_reason"] = "Duplicate (Speed)"
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertTrue(is_valid)

    def test_empty_techniques_or_lessons(self):
        meta = self.valid_meta.copy()
        meta["techniques"] = []
        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(is_valid)
        self.assertTrue(any("techniques" in e for e in errors))


class TestStatisticsEngine(unittest.TestCase):
    """Tests summary KPIs, win rates, duplicate rates, and breakdowns."""

    def test_statistics_calculations(self):
        records = [
            BountyRecord(
                id="KB-2026-001",
                title="IDOR in Billing",
                target="Target Alpha",
                platform="HackerOne",
                date="2026-01-10",
                type="success",
                status="Rewarded",
                severity="High",
                cvss_score=8.5,
                bounty_payout=3000.0,
                vuln_class="CWE-639: IDOR",
                root_cause_category="Access Control",
                failure_reason=None,
                techniques=["parameter-tampering"],
                lessons_learned=["Test batch exports"],
            ),
            BountyRecord(
                id="KB-2026-002",
                title="Race in Checkout",
                target="Target Beta",
                platform="Bugcrowd",
                date="2026-02-15",
                type="failure",
                status="Duplicate",
                severity="Medium",
                cvss_score=5.0,
                bounty_payout=0.0,
                vuln_class="CWE-362: Race Condition",
                root_cause_category="Race Condition",
                failure_reason="Duplicate (Speed)",
                techniques=["parallel-requests", "parameter-tampering"],
                lessons_learned=["Speed matters"],
            ),
            BountyRecord(
                id="TGT-GAMMA-01",
                title="Target Profile Gamma",
                target="Target Gamma",
                platform="Intigriti",
                date="2026-03-01",
                type="target_profile",
                status="Hunting",
                severity="None",
                cvss_score=None,
                bounty_payout=0.0,
                vuln_class="N/A",
                root_cause_category="N/A",
                failure_reason=None,
                techniques=["recon"],
                lessons_learned=["Active research"],
            ),
        ]

        stats = compute_statistics(records)
        self.assertEqual(stats["total_earnings_usd"], 3000.0)
        self.assertEqual(stats["total_records"], 3)
        self.assertEqual(stats["total_resolved"], 2)  # Rewarded + Duplicate
        self.assertEqual(stats["total_rewarded"], 1)
        self.assertEqual(stats["total_duplicates"], 1)
        self.assertEqual(stats["win_rate_percent"], 50.0)
        self.assertEqual(stats["duplicate_rate_percent"], 50.0)
        self.assertEqual(stats["average_reward_usd"], 3000.0)
        self.assertEqual(stats["counts_by_platform"]["HackerOne"], 1)
        self.assertEqual(stats["counts_by_platform"]["Bugcrowd"], 1)
        self.assertEqual(stats["bounty_by_platform"]["HackerOne"], 3000.0)
        self.assertEqual(stats["top_techniques"]["parameter-tampering"], 2)

    def test_zero_resolved_records(self):
        records = [
            BountyRecord(
                id="TGT-TEST-01",
                title="Target Profile",
                target="Test Target",
                platform="HackerOne",
                date="2026-01-01",
                type="target_profile",
                status="Hunting",
                severity="None",
                cvss_score=None,
                bounty_payout=0.0,
                vuln_class="N/A",
                root_cause_category="N/A",
                failure_reason=None,
                techniques=["recon"],
                lessons_learned=["Test"],
            )
        ]
        stats = compute_statistics(records)
        self.assertEqual(stats["total_earnings_usd"], 0.0)
        self.assertEqual(stats["total_resolved"], 0)
        self.assertEqual(stats["win_rate_percent"], 0.0)
        self.assertEqual(stats["duplicate_rate_percent"], 0.0)
        self.assertEqual(stats["average_reward_usd"], 0.0)


class TestCLICommands(unittest.TestCase):
    """Tests CLI commands: validate, reindex, stats, new."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Copy templates and sample files to temp dir
        src_root = Path(__file__).resolve().parent.parent
        shutil.copytree(src_root / "templates", self.repo_root / "templates")
        shutil.copytree(src_root / "knowledge-base", self.repo_root / "knowledge-base")
        shutil.copytree(src_root / "targets", self.repo_root / "targets")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cmd_validate_success(self):
        code = cmd_validate(self.repo_root)
        self.assertEqual(code, 0)

    def test_cmd_validate_failure(self):
        # Create an invalid file
        bad_file = self.repo_root / "knowledge-base" / "successes" / "KB-BAD.md"
        bad_file.write_text(
            """---
id: INVALID_ID
title: Bad
platform: HackerOne
---
Body
""",
            encoding="utf-8",
        )
        code = cmd_validate(self.repo_root)
        self.assertEqual(code, 1)

    def test_cmd_reindex(self):
        code = cmd_reindex(self.repo_root)
        self.assertEqual(code, 0)

        json_path = self.repo_root / "knowledge-base" / "INDEX.json"
        md_path = self.repo_root / "knowledge-base" / "INDEX.md"

        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())

        # Verify JSON
        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertGreaterEqual(data["total_records"], 4)
        self.assertIn("metrics", data)
        self.assertIn("records", data)

        # Verify Markdown
        md_text = md_path.read_text(encoding="utf-8")
        self.assertIn("# Bug Bounty Knowledge Base Index & Analytics", md_text)
        self.assertIn("Executive Performance Summary", md_text)
        self.assertIn("KB-2026-001", md_text)

    def test_cmd_stats(self):
        code = cmd_stats(self.repo_root)
        self.assertEqual(code, 0)

    def test_cmd_new_scaffold(self):
        code = cmd_new(
            repo_root=self.repo_root,
            doc_type="success",
            record_id="KB-2026-900",
            title="Brand New Finding",
            target="Acme Test",
            platform="HackerOne",
            force=False,
        )
        self.assertEqual(code, 0)

        new_file = self.repo_root / "knowledge-base" / "successes" / "KB-2026-900.md"
        self.assertTrue(new_file.exists())

        content = new_file.read_text(encoding="utf-8")
        self.assertIn("id: KB-2026-900", content)
        self.assertIn("Brand New Finding", content)
        self.assertIn("Acme Test", content)

        # Scaffolding again without force should fail
        code_fail = cmd_new(
            repo_root=self.repo_root,
            doc_type="success",
            record_id="KB-2026-900",
            force=False,
        )
        self.assertEqual(code_fail, 1)

        # Scaffolding with force should succeed
        code_force = cmd_new(
            repo_root=self.repo_root,
            doc_type="success",
            record_id="KB-2026-900",
            title="Overwritten Finding",
            force=True,
        )
        self.assertEqual(code_force, 0)
        self.assertIn("Overwritten Finding", new_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
