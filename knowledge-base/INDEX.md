# Bug Bounty Knowledge Base Index & Analytics
*Auto-compiled on 2026-10-31 02:50:04 UTC*

## Executive Performance Summary

- **Total Payout Earnings:** `$3,000.00`
- **Win Rate (Rewarded / Resolved):** `50.0%` (1/2)
- **Duplicate Rate:** `50.0%` (1/2)
- **Average Bounty per Rewarded Bug:** `$3,000.00`
- **Total Tracked Records:** `4`

---

## Platform Breakdown

| Platform | Findings | Total Bounty ($) | Avg Bounty ($) |
| :--- | :---: | :---: | :---: |
| Bugcrowd | 1 | $0.00 | $0.00 |
| HackerOne | 2 | $3,000.00 | $1,500.00 |
| Other | 1 | $0.00 | $0.00 |

## Vulnerability Class Breakdown

| Vulnerability Class | Count | Total Bounty ($) |
| :--- | :---: | :---: |
| CWE-362: Race Condition | 1 | $0.00 |
| CWE-639: IDOR | 2 | $3,000.00 |
| N/A | 1 | $0.00 |

## Status Distribution

| Status | Count |
| :--- | :---: |
| Duplicate | 1 |
| Hunting | 2 |
| Rewarded | 1 |

---

## Complete Knowledge Base Inventory

| ID | Title | Target | Platform | Type | Status | Severity | CVSS | Bounty ($) | Vuln Class | Path |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `KB-2026-001` | BOLA / IDOR in Organization Invoice Export Worker | Acme Cloud Services | HackerOne | `success` | `Rewarded` | High | 8.5 | $3,000 | CWE-639: IDOR | [knowledge-base/successes/KB-2026-001.md](../knowledge-base/successes/KB-2026-001.md) |
| `PB-IDOR-01` | Broken Object Level Authorization (IDOR) Tactical Playbook | Universal Web Applications | Other | `playbook` | `Hunting` | High | - | $0 | CWE-639: IDOR | [knowledge-base/vuln-playbooks/idor-access-control.md](../knowledge-base/vuln-playbooks/idor-access-control.md) |
| `TGT-ACME-01` | Acme Cloud Services Target Profile | Acme Cloud Services | HackerOne | `target_profile` | `Hunting` | None | - | $0 | N/A | [targets/TGT-ACME-01.md](../targets/TGT-ACME-01.md) |
| `KB-2026-002` | Duplicate Race Condition on Checkout Voucher Redemption | MegaStore E-Commerce | Bugcrowd | `failure` | `Duplicate` | Medium | 5.3 | $0 | CWE-362: Race Condition | [knowledge-base/failures/KB-2026-002.md](../knowledge-base/failures/KB-2026-002.md) |

---

## Tactical Lessons Learned Archive

### `KB-2026-001` - BOLA / IDOR in Organization Invoice Export Worker (Acme Cloud Services)
- Asynchronous background export workers frequently bypass HTTP API gateway auth filters.
- Always test UUID parameters across multiple organization contexts to identify unvalidated tenancy scopes.

### `PB-IDOR-01` - Broken Object Level Authorization (IDOR) Tactical Playbook (Universal Web Applications)
- Target secondary actions (export, print, sync, restore) rather than primary CRUD routes.
- Test parameter wrapping: arrays, nested JSON, and query string overrides on POST requests.

### `TGT-ACME-01` - Acme Cloud Services Target Profile (Acme Cloud Services)
- Billing and background export queues have historically contained tenant authorization flaws.

### `KB-2026-002` - Duplicate Race Condition on Checkout Voucher Redemption (MegaStore E-Commerce)
- Public promotional campaigns on large e-commerce platforms attract dozens of hunters within 6 hours.
- Automated single-packet race tooling gives specialized hunters a major speed advantage on generic endpoints.
