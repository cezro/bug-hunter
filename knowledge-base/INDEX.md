# Bug Bounty Knowledge Base Index & Analytics
*Auto-compiled on 2026-11-01 12:15:04 UTC*

## Executive Performance Summary

- **Total Payout Earnings:** `$3,000.00`
- **Win Rate (Rewarded / Resolved):** `50.0%` (1/2)
- **Duplicate Rate:** `50.0%` (1/2)
- **Average Bounty per Rewarded Bug:** `$3,000.00`
- **Total Tracked Records:** `12`

---

## Platform Breakdown

| Platform | Findings | Total Bounty ($) | Avg Bounty ($) |
| :--- | :---: | :---: | :---: |
| Bugcrowd | 7 | $0.00 | $0.00 |
| HackerOne | 2 | $3,000.00 | $1,500.00 |
| Other | 3 | $0.00 | $0.00 |

## Vulnerability Class Breakdown

| Vulnerability Class | Count | Total Bounty ($) |
| :--- | :---: | :---: |
| CWE-285: Improper Authorization | 2 | $0.00 |
| CWE-362: Race Condition | 1 | $0.00 |
| CWE-639: IDOR | 2 | $3,000.00 |
| CWE-639: IDOR / BOLA | 1 | $0.00 |
| CWE-918: SSRF / CWE-639: IDOR / AI-Gateway-Abuse | 1 | $0.00 |
| N/A | 5 | $0.00 |

## Status Distribution

| Status | Count |
| :--- | :---: |
| Duplicate | 1 |
| Hunting | 8 |
| In-Triage | 2 |
| Rewarded | 1 |

---

## Complete Knowledge Base Inventory

| ID | Title | Target | Platform | Type | Status | Severity | CVSS | Bounty ($) | Vuln Class | Path |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `KB-2026-001` | BOLA / IDOR in Organization Invoice Export Worker | Acme Cloud Services | HackerOne | `success` | `Rewarded` | High | 8.5 | $3,000 | CWE-639: IDOR | [knowledge-base/successes/KB-2026-001.md](../knowledge-base/successes/KB-2026-001.md) |
| `PB-IDOR-01` | Broken Object Level Authorization (IDOR) Tactical Playbook | Universal Web Applications | Other | `playbook` | `Hunting` | High | - | $0 | CWE-639: IDOR | [knowledge-base/vuln-playbooks/idor-access-control.md](../knowledge-base/vuln-playbooks/idor-access-control.md) |
| `TGT-ACME-01` | Acme Cloud Services Target Profile | Acme Cloud Services | HackerOne | `target_profile` | `Hunting` | None | - | $0 | N/A | [targets/TGT-ACME-01.md](../targets/TGT-ACME-01.md) |
| `KB-2026-002` | Duplicate Race Condition on Checkout Voucher Redemption | MegaStore E-Commerce | Bugcrowd | `failure` | `Duplicate` | Medium | 5.3 | $0 | CWE-362: Race Condition | [knowledge-base/failures/KB-2026-002.md](../knowledge-base/failures/KB-2026-002.md) |
| `INV-2026-001` | Arbitrary Enterprise LLM Model Selection & Unauthorized Consumption in Newfold AI Gateway | OneWeb Platform | Bugcrowd | `investigation` | `Hunting` | High | 7.5 | $0 | CWE-285: Improper Authorization | [investigations/INV-2026-001.md](../investigations/INV-2026-001.md) |
| `INV-2026-002` | HostGator LATAM AI Platform Security Evaluation | HostGator LATAM | Bugcrowd | `investigation` | `Hunting` | High | - | $0 | CWE-918: SSRF / CWE-639: IDOR / AI-Gateway-Abuse | [investigations/INV-2026-002.md](../investigations/INV-2026-002.md) |
| `PB-CHAIN-01` | Multi-Stage Attack Chain Correlation & Vulnerability Prioritization | Global | Other | `playbook` | `Hunting` | High | - | $0 | N/A | [knowledge-base/vuln-playbooks/PB-CHAIN-01.md](../knowledge-base/vuln-playbooks/PB-CHAIN-01.md) |
| `PB-RECON-01` | Continuous Automated Recon & Attack Surface Monitoring | Global | Other | `playbook` | `Hunting` | High | - | $0 | N/A | [knowledge-base/vuln-playbooks/PB-RECON-01.md](../knowledge-base/vuln-playbooks/PB-RECON-01.md) |
| `REP-2026-001` | Improper Authorization in POST /ai-api/v3.0/chat allows Arbitrary Enterprise LLM Deployment Selection and Quota Exhaustion | OneWeb Platform | Bugcrowd | `report` | `In-Triage` | High | 7.1 | $0 | CWE-285: Improper Authorization | [reports/REP-2026-001.md](../reports/REP-2026-001.md) |
| `REP-2026-002` | BOLA in AI Agent Credentials Endpoint leads to AWS AppSync Session Token Exposure | HostGator LATAM | Bugcrowd | `report` | `In-Triage` | High | 8.5 | $0 | CWE-639: IDOR / BOLA | [reports/REP-2026-002.md](../reports/REP-2026-002.md) |
| `TGT-HG-LATAM-01` | HostGator LATAM Profile | HostGator LATAM | Bugcrowd | `target_profile` | `Hunting` | None | - | $0 | N/A | [targets/TGT-HG-LATAM-01.md](../targets/TGT-HG-LATAM-01.md) |
| `TGT-ONEWEB-01` | OneWeb Platform Profile (Web.com & Newfold Digital) | Web.com Group / Newfold Digital | Bugcrowd | `target_profile` | `Hunting` | None | - | $0 | N/A | [targets/TGT-ONEWEB-01.md](../targets/TGT-ONEWEB-01.md) |

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

### `INV-2026-001` - Arbitrary Enterprise LLM Model Selection & Unauthorized Consumption in Newfold AI Gateway (OneWeb Platform)
- AI Gateways often expose internal deployment parameters directly in client request bodies without server-side policy enforcement.

### `INV-2026-002` - HostGator LATAM AI Platform Security Evaluation (HostGator LATAM)
- SuperGator AI platform communicates with backend at https://ai-core.hostgator.com.br/api.
- AWS AppSync GraphQL WebSocket is used for real-time agent events and temporary STS credentials issuance.

### `PB-CHAIN-01` - Multi-Stage Attack Chain Correlation & Vulnerability Prioritization (Global)
- Isolated Medium findings often get closed as informative; chaining two Medium findings into an end-to-end exploit unlocks High/Critical bounties.
- Always tailor tooling and probing parameters to the detected technology stack rather than firing generic payloads.
- Enforce adaptive timing profiles (e.g., Conservative/Stealth) when Cloudflare or Akamai is detected to prevent IP bans.

### `PB-RECON-01` - Continuous Automated Recon & Attack Surface Monitoring (Global)
- Automation replaces repetitive busywork; hackers win bug bounties by catching new and untested assets first.
- Never run full port scans on hundreds of hosts upfront; use smart two-tiered scanning (top 1000 first, full ports only on anomalies).
- Visual recon via automated screenshots enables spotting internal portals and staging APIs in seconds instead of hours.

### `REP-2026-001` - Improper Authorization in POST /ai-api/v3.0/chat allows Arbitrary Enterprise LLM Deployment Selection and Quota Exhaustion (OneWeb Platform)
- Client-supplied deployment identifiers must never be forwarded directly to backend LLM cloud endpoints.

### `REP-2026-002` - BOLA in AI Agent Credentials Endpoint leads to AWS AppSync Session Token Exposure (HostGator LATAM)
- SuperGator AI platform exposes direct IAM credential generation endpoints per agentId.
- Object-level authorization must be enforced in Laravel policy prior to STS credential synthesis.

### `TGT-HG-LATAM-01` - HostGator LATAM Profile (HostGator LATAM)
- Target has newly prioritized AI Agents and AI-driven VPS features.
- carrinho.hostgator.com.br is explicitly out of scope per brief update.

### `TGT-ONEWEB-01` - OneWeb Platform Profile (Web.com & Newfold Digital) (Web.com Group / Newfold Digital)
- OneWeb is a shared white-label platform across Web.com, Network Solutions, Bluehost, and HostGator.
- IdentityServer4 (ids4.builderservices.io) federates all microservice tokens and AI scopes.
