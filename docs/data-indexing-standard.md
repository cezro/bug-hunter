# Bug Bounty Knowledge Base & Data Indexing Standard
**Version:** 1.0.0  
**Effective Date:** 2026-10-31  
**Status:** Active / Enforced  

---

## 1. Overview & Objectives

The Bug Bounty Knowledge Base (KB) and Data Indexing Architecture provides a unified, structured, and searchable repository for bug bounty reconnaissance, vulnerability investigations, submitted reports, post-mortem analyses, and tactical playbooks.

### Key Objectives
1. **Systematic Knowledge Retention:** Transform single-instance discoveries and edge-case bypasses into durable, searchable tactical assets.
2. **Post-Mortem Driven Improvement:** Ruthlessly analyze both bounty payouts (successes) and rejected/duplicate reports (failures) to improve triage velocity and win rates.
3. **Automated Metrics & Analytics:** Provide real-time computation of bounty earnings, win rates, duplicate rates, vulnerability distribution, and target platform ROI.
4. **Agent & Human Interoperability:** Ensure that human security researchers and AI swarm subagents (`bb-methodology`, `agent-reach`, `bug-hunt-swarm`, `triage-validation`, `report-writing`, etc.) operate against consistent metadata schemas and deterministic validation.

---

## 2. Directory Layout & Storage Hierarchy

All records in the repository reside in standard root directories:

```
├── docs/
│   └── data-indexing-standard.md        # This specification
├── knowledge-base/
│   ├── INDEX.json                       # Machine-readable compiled index
│   ├── INDEX.md                         # Human-readable compiled index & analytics
│   ├── successes/                       # Rewarded reports & post-mortems (KB-YYYY-XXX.md)
│   ├── failures/                        # Duplicate / rejected post-mortems (KB-YYYY-XXX.md)
│   └── vuln-playbooks/                  # Vulnerability class playbooks (slug.md)
├── targets/                             # Target program profiles (TGT-SLUG-XX.md)
├── investigations/                      # Active hunting notes (INV-YYYY-XXX.md)
├── reports/                             # Final drafted bounty reports (REP-YYYY-XXX.md)
├── templates/                           # Standard authoring templates
├── scripts/
│   └── index_manager.py                 # CLI tool for indexing, validation, stats & generation
└── tests/
    └── test_index_manager.py            # Automated test suite
```

---

## 3. Frontmatter Metadata Specification

Every markdown record tracked by the indexing system must begin with YAML frontmatter bounded by `---` delimiters.

### 3.1 Field Definitions & Schema

| Field | Type | Required | Allowed Values / Constraints | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `string` | **Yes** | Pattern: `^(KB\|TGT\|REP\|INV\|PB)-[A-Za-z0-9_-]+$` | Unique identifier for the record. |
| `title` | `string` | **Yes** | 5 to 140 characters, single line | Concise descriptive title of the finding or record. |
| `target` | `string` | **Yes** | Non-empty string (e.g. `Acme Corp`, `Shopify`) | Name of target organization or program. |
| `platform` | `string` | **Yes** | `HackerOne`, `Bugcrowd`, `Intigriti`, `Immunefi`, `Direct/Private`, `Other` | Bug bounty platform host or engagement model. |
| `date` | `string` | **Yes** | Format: `YYYY-MM-DD` | Date of discovery, submission, or creation. |
| `type` | `string` | **Yes** | `success`, `failure`, `target_profile`, `investigation`, `playbook`, `report` | Category classification of the record. |
| `status` | `string` | **Yes** | `Hunting`, `In-Triage`, `Rewarded`, `Duplicate`, `Informative`, `Rejected`, `Out-of-Scope` | Current operational lifecycle status. |
| `severity` | `string` | **Yes** | `Critical`, `High`, `Medium`, `Low`, `None` | Assessed or awarded severity level. |
| `cvss_score` | `float \| null` | **Yes** | `0.0` to `10.0` or `null` | CVSS v3.1 base score (e.g., `8.5`). |
| `bounty_payout` | `number` | **Yes** | Integer or float >= 0 | Bounty amount in USD (0 for unrewarded / pending). |
| `vuln_class` | `string` | **Yes** | CWE identifier & name (e.g. `CWE-639: IDOR`, or `N/A`) | Vulnerability classification according to CWE. |
| `root_cause_category`| `string` | **Yes** | `Access Control`, `Business Logic`, `Input Validation`, `Authentication`, `Configuration`, `Race Condition`, `Information Disclosure`, `N/A` | Fundamental software defect category. |
| `failure_reason` | `string \| null`| Conditional | `Duplicate (Speed)`, `Out of Scope`, `By Design / Informative`, `WAF / Mitigated`, `Insufficient Impact`, or `null` | Root cause for unrewarded or closed report. Required when `type: failure` or status is `Duplicate` / `Rejected` / `Out-of-Scope` / `Informative`. |
| `techniques` | `list[string]` | **Yes** | Non-empty list of tags | Specific offensive vectors (e.g., `[parameter-tampering, jwt-replay]`). |
| `lessons_learned` | `list[string]` | **Yes** | 1 to 3 concise bullet strings | Tactical takeaways for methodology refinement. |

---

## 4. Conditional Validation Rules

The `index_manager.py` validator enforces strict invariant rules:

1. **Failure Justification Rule:**  
   If `type == "failure"` or `status` is one of `{"Duplicate", "Rejected", "Out-of-Scope", "Informative"}`, `failure_reason` **MUST NOT** be `null` and must match one of the standard failure reasons.
2. **Bounty Consistency Rule:**  
   If `status == "Rewarded"`, `bounty_payout` must be strictly greater than 0. If `status` is one of `{"Duplicate", "Rejected", "Out-of-Scope", "Informative", "Hunting", "In-Triage"}`, `bounty_payout` must be strictly 0.
3. **Score Boundary Rule:**  
   `cvss_score` must fall strictly within `0.0 <= cvss_score <= 10.0`, or be set to `null` if CVSS is not applicable (e.g., target profiles or playbooks).
4. **Identifier Namespace Standard:**
   - `KB-YYYY-XXX`: Knowledge Base post-mortems (success or failure)
   - `TGT-<SLUG>-XX`: Target program profiles
   - `REP-YYYY-XXX`: Bounty submission reports
   - `INV-YYYY-XXX`: Active vulnerability investigations
   - `PB-<SLUG>`: Attack playbooks

---

## 5. Frontmatter Example

```yaml
---
id: KB-2026-001
title: Broken Object Level Authorization on Invoice Export API
target: Acme Fintech Corp
platform: HackerOne
date: 2026-03-15
type: success
status: Rewarded
severity: High
cvss_score: 8.5
bounty_payout: 3000
vuln_class: "CWE-639: IDOR"
root_cause_category: Access Control
failure_reason: null
techniques:
  - parameter-tampering
  - uuid-enumeration
  - horizontal-privilege-escalation
lessons_learned:
  - "Always check secondary REST endpoints (export, pdf, print) for missing tenant tenancy checks."
  - "Replacing tenant UUID with sequential integer IDs frequently triggers legacy backend routes."
---
```

---

## 6. Document Body Structure Standards

### 6.1 Success Post-Mortem (`knowledge-base/successes/`)
1. **Summary & Executive Briefing**: Short recap of what was found, who was impacted, and reward details.
2. **Vulnerability Mechanics**: Detailed technical description of endpoint, parameters, and flawed logic.
3. **Proof of Concept (HTTP Raw)**: Minimal reproducible HTTP request and response trace.
4. **Remediation & Defense**: How the vendor patched the defect (authorizer filter, database scope check).
5. **Hunter Takeaways**: What made this discovery possible and how to automate the pattern.

### 6.2 Failure Post-Mortem (`knowledge-base/failures/`)
1. **Failure Taxonomy**: Exact reason for rejection / duplicate.
2. **Timeline Analysis**: Time from feature launch -> discovery -> submission -> triage closure.
3. **Root Cause of Failure**: Why did another researcher submit first? Why did the triage team determine it was intended behavior?
4. **Process Improvements**: Specific automation or recon adjustments to prevent recurring failure.

### 6.3 Target Profile (`targets/`)
1. **Program Overview & Policy Scope**: In-scope domains, wildcards, out-of-scope services, and Safe Harbor status.
2. **Tech Stack & Architecture**: Cloud providers, frameworks, identity providers (IdP), and API formats (GraphQL/REST).
3. **High-Value Assets**: Prime business logic areas (billing, payouts, admin consoles, permissions).
4. **Historical Disclosures & Researcher Intel**: Past resolved bugs and known developer tendencies.

### 6.4 Playbook (`knowledge-base/vuln-playbooks/`)
1. **Vulnerability Overview**: Core CWE explanation and impact.
2. **Attack Surface Discovery**: How to find target endpoints across large scopes.
3. **Test Vectors & Bypass Patterns**: Concrete parameter tweaks, headers, encodings, and race windows.
4. **Automation & Tooling**: CLI commands and payload templates.

---

## 7. Lifecycle & Tooling Automation

The knowledge base is continuously indexed and validated via the `scripts/index_manager.py` tool.

- **Pre-commit / CI Validation:** `python scripts/index_manager.py validate` fails on any schema or enum violation.
- **Auto-compilation:** `python scripts/index_manager.py reindex` compiles `INDEX.json` and updates `INDEX.md`.
- **Analytics:** `python scripts/index_manager.py stats` renders platform earnings, win rate, and vuln class breakdown.
- **Scaffolding:** `python scripts/index_manager.py new <type> <id>` generates compliant boilerplate.
