#!/usr/bin/env python3
"""
Adversarial Stress-Testing Suite for Bug Bounty Knowledge Base & Data Indexing Manager.
Authored by: Disprover Subagent

This suite proves edge cases, invariant bypasses, security vulnerabilities,
and parsing defects in `scripts/index_manager.py` and repository templates.
"""

from __future__ import annotations

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


class TestAdversarialSecurityAndPathTraversal(unittest.TestCase):
    """Stress tests for file system boundaries and path traversal."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir(parents=True)
        (self.templates_dir / "post_mortem_success.md").write_text(
            "---\nid: {{ID}}\ntitle: {{TITLE}}\nplatform: HackerOne\n---\nBody",
            encoding="utf-8",
        )

    def tearDown(self):
        (self.temp_dir.parent / "traversal_exploit.md").unlink(missing_ok=True)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cmd_new_rejects_path_traversal_in_id(self):
        """
        FAILING TEST:
        Proves that cmd_new accepts path traversal in record_id and writes files
        outside the designated directory / repository root.
        """
        traversal_id = "../../../traversal_exploit"
        result = cmd_new(
            repo_root=self.temp_dir,
            doc_type="success",
            record_id=traversal_id,
        )
        # It should reject invalid IDs containing traversal characters and return non-zero
        self.assertNotEqual(
            result,
            0,
            "cmd_new permitted path traversal in record_id!",
        )
        # Ensure no file was created outside repo root
        escaped_file = self.temp_dir.parent / "traversal_exploit.md"
        self.assertFalse(
            escaped_file.exists(),
            f"Arbitrary file write confirmed: {escaped_file} was created outside repo root!",
        )


class TestAdversarialYAMLParserEdgeCases(unittest.TestCase):
    """Stress tests for YAML frontmatter parser edge cases."""

    def test_empty_yaml_key_causes_type_error_in_validator(self):
        """
        FAILING TEST:
        Proves that empty YAML fields (e.g. 'failure_reason:') are parsed as empty lists [],
        which then crashes `validate_record_metadata` with unhandled TypeError (unhashable type: 'list')
        when testing membership against set constants.
        """
        raw = """---
id: KB-2026-001
title: "SQL Injection in User Profile"
target: Acme Corp
platform: HackerOne
date: 2026-01-01
type: success
status: Rewarded
severity: High
cvss_score: 8.5
bounty_payout: 2500
vuln_class: "CWE-89: SQLi"
root_cause_category: Input Validation
failure_reason:
techniques:
  - sqli-error-based
lessons_learned:
  - "Sanitize inputs"
---
Body
"""
        meta, _ = parse_frontmatter(raw)
        # An empty YAML field without list items must resolve to None, not []
        self.assertIsNone(
            meta.get("failure_reason"),
            f"Expected empty YAML field to parse as None, but got: {meta.get('failure_reason')!r}",
        )

        # It must not crash validate_record_metadata
        try:
            is_valid, errors = validate_record_metadata(meta, "test.md")
        except TypeError as e:
            self.fail(f"validate_record_metadata crashed with TypeError on empty key: {e}")

    def test_quoted_string_with_hash_and_comment_truncation(self):
        """
        FAILING TEST:
        Proves that a quoted string containing a '#' followed by an inline comment
        is corrupted because .find('#') searches inside the quotes.
        """
        raw = """---
id: KB-2026-001
title: "Critical Issue #42: Authentication Bypass" # Security Audit Finding
target: Acme Corp
platform: HackerOne
date: 2026-01-01
type: success
status: Rewarded
severity: Critical
cvss_score: 9.8
bounty_payout: 5000
vuln_class: "CWE-287"
root_cause_category: Authentication
failure_reason: null
techniques:
  - auth-bypass
lessons_learned:
  - "Verify tokens"
---
Body
"""
        meta, _ = parse_frontmatter(raw)
        # The title should preserve the full quoted text and only strip the external comment
        self.assertEqual(
            meta["title"],
            "Critical Issue #42: Authentication Bypass",
            f"Quoted string was corrupted/truncated at '#' inside quotes! Got: {meta['title']!r}",
        )

    def test_utf8_bom_handling(self):
        """
        FAILING TEST:
        Proves that files encoded with UTF-8-BOM (common on Windows PowerShell/Notepad)
        fail to parse with ValueError due to regex expecting start of string without BOM.
        """
        bom_raw = "\ufeff---\nid: KB-2026-001\ntitle: Test Finding\n---\nBody"
        try:
            meta, _ = parse_frontmatter(bom_raw)
            self.assertEqual(meta["id"], "KB-2026-001")
        except ValueError as e:
            self.fail(f"parse_frontmatter failed on UTF-8 BOM: {e}")

    def test_missing_trailing_newline_on_closing_delimiter(self):
        """
        FAILING TEST:
        Proves that frontmatter without a trailing newline after the closing '---'
        raises ValueError instead of being accepted.
        """
        raw_no_newline = "---\nid: KB-2026-001\ntitle: Test\n---"
        try:
            meta, body = parse_frontmatter(raw_no_newline)
            self.assertEqual(meta["id"], "KB-2026-001")
        except ValueError as e:
            self.fail(f"parse_frontmatter failed when closing delimiter has no trailing newline: {e}")

    def test_trailing_whitespace_on_delimiter(self):
        """
        FAILING TEST:
        Proves that trailing spaces after '--- ' break delimiter recognition.
        """
        raw_trailing_space = "--- \nid: KB-2026-001\ntitle: Test\n--- \nBody"
        try:
            meta, _ = parse_frontmatter(raw_trailing_space)
            self.assertEqual(meta["id"], "KB-2026-001")
        except ValueError as e:
            self.fail(f"parse_frontmatter failed when delimiters contain trailing spaces: {e}")

    def test_single_quoted_comma_in_inline_list(self):
        """
        FAILING TEST:
        Proves that single-quoted list items containing commas are improperly split
        because the regex only handles double quotes.
        """
        raw = """---
id: KB-2026-001
techniques: ['param, tamper', 'test']
---
Body
"""
        meta, _ = parse_frontmatter(raw)
        self.assertEqual(
            meta["techniques"],
            ["param, tamper", "test"],
            f"Inline list regex failed on single quotes with commas! Got: {meta['techniques']!r}",
        )

    def test_multiline_list_trailing_comments_stripped(self):
        """
        FAILING TEST:
        Proves that inline comments on multiline list items (- item # comment)
        are not stripped and pollute the tag values.
        """
        raw = """---
id: KB-2026-001
techniques:
  - parameter-tampering # Primary vector
  - idor # Secondary vector
---
Body
"""
        meta, _ = parse_frontmatter(raw)
        self.assertEqual(
            meta["techniques"],
            ["parameter-tampering", "idor"],
            f"Comments were not stripped from multiline list items! Got: {meta['techniques']!r}",
        )


class TestAdversarialValidationInvariants(unittest.TestCase):
    """Stress tests for business logic invariants and schema validation."""

    def setUp(self):
        self.base_valid = {
            "id": "KB-2026-001",
            "title": "Valid Finding Title",
            "target": "Target Org",
            "platform": "HackerOne",
            "date": "2026-01-01",
            "type": "success",
            "status": "Rewarded",
            "severity": "High",
            "cvss_score": 8.0,
            "bounty_payout": 2000.0,
            "vuln_class": "CWE-639: IDOR",
            "root_cause_category": "Access Control",
            "failure_reason": None,
            "techniques": ["parameter-tampering"],
            "lessons_learned": ["Test all endpoints"],
        }

    def test_rewarded_status_cannot_have_zero_bounty(self):
        """
        FAILING TEST:
        Per data-indexing-standard.md Section 4 Rule 2 (Bounty Consistency Rule):
        'If status == "Rewarded", bounty_payout must be greater than 0'.
        Currently, bounty_payout: 0 with status: Rewarded passes validation.
        """
        meta = self.base_valid.copy()
        meta["status"] = "Rewarded"
        meta["bounty_payout"] = 0.0

        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed status='Rewarded' with bounty_payout=0 without justification!",
        )
        self.assertTrue(
            any("Rewarded" in e and "bounty_payout" in e for e in errors),
            f"Expected error message regarding Rewarded with 0 payout, got: {errors}",
        )

    def test_duplicate_status_cannot_have_positive_bounty(self):
        """
        FAILING TEST:
        Proves that unrewarded/failed statuses (Duplicate, Rejected, Out-of-Scope)
        can specify positive bounty payouts (e.g. $5,000), which corrupts financial metrics.
        """
        meta = self.base_valid.copy()
        meta["type"] = "failure"
        meta["status"] = "Duplicate"
        meta["failure_reason"] = "Duplicate (Speed)"
        meta["bounty_payout"] = 5000.0  # Invalid! Duplicates do not receive payouts.

        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed status='Duplicate' with bounty_payout=5000!",
        )

    def test_nan_and_inf_bounty_payout_rejected(self):
        """
        FAILING TEST:
        Proves that float('nan') and float('inf') bypass the bounty_payout >= 0 check
        because NaN comparisons in Python return False for (nan < 0).
        """
        for bad_payout in [float("nan"), float("inf")]:
            meta = self.base_valid.copy()
            meta["bounty_payout"] = bad_payout
            is_valid, errors = validate_record_metadata(meta, "test.md")
            self.assertFalse(
                is_valid,
                f"Validator allowed non-finite bounty_payout: {bad_payout}!",
            )

    def test_unhashable_element_in_techniques_list(self):
        """
        FAILING TEST:
        Proves that nested dictionaries or non-strings in `techniques`
        pass `validate_record_metadata` and then crash `compute_statistics` with TypeError.
        """
        meta = self.base_valid.copy()
        meta["techniques"] = [{"nested": "dict"}]  # Invalid tag type

        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed dictionary elements inside techniques list!",
        )

    def test_title_maximum_length_and_multiline(self):
        """
        FAILING TEST:
        Per data-indexing-standard.md Section 3.1:
        Title must be '5 to 140 characters, single line'.
        Currently, >140 characters and multiline strings pass validation.
        """
        # Test > 140 characters
        meta_too_long = self.base_valid.copy()
        meta_too_long["title"] = "A" * 150
        is_valid, errors = validate_record_metadata(meta_too_long, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed title longer than 140 characters!",
        )

        # Test multiline title
        meta_multiline = self.base_valid.copy()
        meta_multiline["title"] = "Line 1\nLine 2 Title"
        is_valid, errors = validate_record_metadata(meta_multiline, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed multiline title!",
        )

    def test_id_prefix_matches_document_type(self):
        """
        FAILING TEST:
        Per data-indexing-standard.md Section 4 Rule 4:
        - KB-* for success / failure
        - TGT-* for target_profile
        - INV-* for investigation
        - PB-* for playbook
        Currently, any prefix is accepted for any type.
        """
        meta = self.base_valid.copy()
        meta["type"] = "target_profile"
        meta["id"] = "KB-2026-999"  # Mismatched prefix

        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed type='target_profile' with ID prefix 'KB-'!",
        )

    def test_rewarded_status_cannot_have_failure_reason(self):
        """
        FAILING TEST:
        Proves that status='Rewarded' can coexist with a failure_reason like
        'Duplicate (Speed)', which is a contradictory state.
        """
        meta = self.base_valid.copy()
        meta["status"] = "Rewarded"
        meta["failure_reason"] = "Duplicate (Speed)"

        is_valid, errors = validate_record_metadata(meta, "test.md")
        self.assertFalse(
            is_valid,
            "Validator allowed status='Rewarded' with non-null failure_reason!",
        )


class TestAdversarialScaffoldingAndTemplates(unittest.TestCase):
    """Stress tests for scaffolding CLI (cmd_new) and template consistency."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        src_root = Path(__file__).resolve().parent.parent
        shutil.copytree(src_root / "templates", self.temp_dir / "templates")

    def tearDown(self):
        (self.temp_dir.parent / "traversal_exploit.md").unlink(missing_ok=True)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cmd_new_platform_flag_is_respected(self):
        """
        FAILING TEST:
        Proves that passing --platform (e.g. Immunefi or Intigriti) to cmd_new is
        silently ignored because templates hardcode 'platform: HackerOne'.
        """
        cmd_new(
            repo_root=self.temp_dir,
            doc_type="target_profile",
            record_id="TGT-TEST-01",
            platform="Immunefi",
        )
        created_file = self.temp_dir / "targets" / "TGT-TEST-01.md"
        content = created_file.read_text(encoding="utf-8")
        self.assertIn(
            "platform: Immunefi",
            content,
            "cmd_new ignored --platform flag and preserved hardcoded template platform!",
        )

    def test_cmd_new_playbook_scaffolds_playbook_not_rewarded_success(self):
        """
        FAILING TEST:
        Proves that `cmd_new playbook PB-XSS` uses post_mortem_success.md,
        scaffolding a record with type='success', status='Rewarded', and $3,000 bounty!
        """
        cmd_new(
            repo_root=self.temp_dir,
            doc_type="playbook",
            record_id="PB-XSS-01",
        )
        created_file = self.temp_dir / "knowledge-base" / "vuln-playbooks" / "PB-XSS-01.md"
        content = created_file.read_text(encoding="utf-8")
        self.assertIn(
            "type: playbook",
            content,
            "cmd_new playbook scaffolded with wrong type (copied post_mortem_success.md)!",
        )
        self.assertIn(
            "bounty_payout: 0",
            content,
            "cmd_new playbook scaffolded with positive $3,000 bounty payout!",
        )


class TestAdversarialMarkdownTableGeneration(unittest.TestCase):
    """Stress tests for Markdown table rendering with special characters."""

    def test_pipe_character_in_title_or_target_escaped(self):
        r"""
        FAILING TEST:
        Proves that pipe characters '|' in record titles break markdown table structure
        because they are not escaped as '\|'.
        """
        record = BountyRecord(
            id="KB-2026-001",
            title="SSRF | Cloud Metadata Exfiltration via PDF Export",
            target="Acme Corp | Internal Services",
            platform="HackerOne",
            date="2026-01-01",
            type="success",
            status="Rewarded",
            severity="High",
            cvss_score=8.5,
            bounty_payout=3000.0,
            vuln_class="CWE-918: SSRF",
            root_cause_category="Input Validation",
            failure_reason=None,
            techniques=["ssrf"],
            lessons_learned=["Test PDF parser"],
            file_path="knowledge-base/successes/KB-2026-001.md",
        )
        stats = compute_statistics([record])
        md = generate_index_markdown([record], stats)

        # In markdown table rows, unescaped pipe characters in cells corrupt column count.
        for line in md.splitlines():
            if line.startswith("| `KB-2026-001`"):
                # Total expected columns: 11 (separated by 12 pipes: leading, trailing, 10 internal)
                # Escaped pipes \| do not split columns, but unescaped pipes do!
                # Replace escaped pipes before counting splits
                cleaned = line.replace(r"\|", "__ESCAPED_PIPE__")
                pipe_count = cleaned.count("|")
                self.assertEqual(
                    pipe_count,
                    12,
                    f"Markdown table row contains unescaped pipes resulting in {pipe_count} pipe delimiters (expected 12)!\nLine: {line}",
                )


if __name__ == "__main__":
    unittest.main()
