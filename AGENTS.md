# Agent Operational Guide: Bug Bounty Swarm Protocol

**Target Audience:** Autonomous Agents, Swarm Subagents (`prover`, `disprover`, `bug-hunt-swarm`), and Human Operators.  
**Version:** 1.0.0  
**Effective Date:** 2026-10-31  

---

## 1. Core Architecture & Operating Principles

This repository acts as the shared intelligence hub, methodology repository, and analytics ledger for bug bounty operations. When hunting on bug bounty programs, agents operate as a **Dialectic Multi-Agent Swarm** governed by strict safety rules, deterministic verification gates, and continuous indexing.

```
       +-----------------------------------------------------------+
       |                  User / Operator Intake                   |
       |             (Program URL, Scope, Credentials)             |
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
       |               STEP 1: Intake & Scope Setup                |
       |  - Scaffolds targets/TGT-<ID>.md via index_manager.py     |
       |  - Validates Safe Harbor & Out-of-Scope constraints       |
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
       |       STEP 2: Diagnostic Recon & Collaborative Hunting    |
       |                                                           |
       |  2.1 Public Intelligence & Writeups  --> agent-reach      |
       |  2.2 Attack Surface & Fingerprints   --> security-bounty- |
       |                                          hunter & bb-meth |
       |  2.3 Deep Anomaly / Root-Cause Inv   --> bug-hunt-swarm   |
       |  2.4 Falsification & 7-Question Gate --> triage-val &     |
       |                                          disprover        |
       |  2.5 Impact-First Report Synthesis   --> report-writing   |
       +-----------------------------+-----------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
       |      POST-TRIAGE: Knowledge Retention & Auto-Indexing     |
       |  - Success/Failure Post-Mortems in knowledge-base/        |
       |  - python scripts/index_manager.py reindex                |
       +-----------------------------------------------------------+
```

---

## 2. Standard 2-Step User Workflow

### Step 1: Program Link / Target Intake
When the user supplies a bug bounty link, policy page, or target briefing:
1. **Initialize Target Profile:**  
   Run:
   ```bash
   python scripts/index_manager.py new target_profile TGT-<PROGRAM_SLUG>-01 --title "<Program Name> Profile" --target "<Program Name>" --platform "<Platform>"
   ```
2. **Safe Harbor & Policy Invariants Verification:**
   - Confirm program platform (`HackerOne`, `Bugcrowd`, `Intigriti`, `Immunefi`, `Direct/Private`).
   - Parse in-scope domains and wildcard patterns (`*.target.com`).
   - Extract strictly forbidden assets (e.g., third-party help desks, payment gateways, staging systems without permission).
   - Verify Safe Harbor tier (Gold / Full Safe Harbor vs Standard).

### Step 2: Diagnostic Recon & Collaborative Hunting
Execute structured, non-destructive reconnaissance and multi-agent exploration across five distinct phases:

#### 2.1 Passive Intelligence & Historical Disclosures
- Route to [`agent-reach`](file:///.agents/skills/agent-reach/SKILL.md) to search public HackerOne disclosures, GitHub commit logs, developer blogs, changelogs, and security advisories related to the target.
- Identify known past vulnerability patterns (e.g., IDOR on user exports, race condition on wallet balance, GraphQL introspection leaks).

#### 2.2 Continuous 3-Pillar Recon & Surface Mapping (CyberFlow Methodology)
- Route to [`security-bounty-hunter`](file:///.agents/skills/security-bounty-hunter/SKILL.md), [`bb-methodology`](file:///.agents/skills/bb-methodology/SKILL.md), and playbook [`PB-RECON-01`](file:///c:/Users/Zero/Documents/GitHub%20Repositories/bug-hunter/knowledge-base/vuln-playbooks/PB-RECON-01.md):
  1. **Subdomain Discovery & 24/7 Delta Monitoring:**
     - Multi-source aggregation (`subfinder`, `amass`, `assetfinder`, `crt.sh`).
     - Daily baseline diffing: `diff(today, yesterday)` to instantly flag new, untested assets (highest probability of bugs).
  2. **Smart Tiered Port Scanning & Liveness Pre-Filtering:**
     - Pre-filter alive hosts with `httpx` (never scan dead hosts).
     - Tier 1: Fast top 1000 ports (~2 min/host).
     - Tier 2: Deep 1-65535 scan exclusively on anomalous listening ports (8080, 8443, 8000, 9000).
     - Automated vulnerability auditing using `nuclei` templates (exposed Git, Swagger/OpenAPI docs, unpatched CVEs).
  3. **Visual Recon & Tech Stack Profiling:**
     - Headless automated screenshot gallery (`EyeWitness` / `scripts/recon_pipeline.py`).
     - Rapid visual triage: identify admin portals, unauthenticated staging APIs, and directory listings in seconds.
     - Tech stack profiling (Wappalyzer / header analysis) to match targets to optimal vulnerability classes.
- Record findings into `targets/TGT-<ID>.md`. Execute via:
  ```bash
  python scripts/recon_pipeline.py <domain> --slug <SLUG>
  ```

#### 2.3 Swarm Root-Cause Exploration & Attack Chain Discovery (HexStrike AI Methodology)
- When anomalous behavior or target fingerprints are detected, run the HexStrike Tactical Decision Engine:
  ```bash
  python scripts/hexstrike_decision.py <domain> --tech <STACK>
  ```
- Route to [`bug-hunt-swarm`](file:///.agents/skills/bug-hunt-swarm/SKILL.md) and playbook [`PB-CHAIN-01`](file:///c:/Users/Zero/Documents/GitHub%20Repositories/bug-hunter/knowledge-base/vuln-playbooks/PB-CHAIN-01.md):
- Scaffold an investigation note:
  ```bash
  python scripts/index_manager.py new investigation INV-2026-XXX --title "<Hypothesis Title>" --target "<Target>"
  ```
- Swarm agents independently investigate and correlate findings according to the **HexStrike 10-Tier Priority Hierarchy**:
  - **Tier 10-9 (Critical):** RCE (SSTI, deserialization) & SQLi.
  - **Tier 8 (High):** IDOR/BOLA, SSRF, AI Gateway Abuse (arbitrary model routing), and Auth Bypass.
  - **Tier 7 (High):** XXE and Business Logic Race Conditions (limit-overruns).
  - **Attack Chain Discovery:** Correlate isolated Medium anomalies (e.g. CORS preauth token leaks + AI model injection) into High/Critical severity chains.

#### 2.4 Pre-Submission Triage & Falsification Gate
- Before drafting any report, route to [`triage-validation`](file:///.agents/skills/triage-validation/SKILL.md).
- Enforce the **7-Question Gate**:
  1. *Is this asset strictly in-scope per target policy?*
  2. *Is this reproducible using two dedicated test accounts without cross-user disruption?*
  3. *Is the impact demonstrated with real data exposure (no "could potentially")?*
  4. *Is this on the target program's Out-of-Scope or Always-Rejected list?*
  5. *Is this a duplicate or already publicly reported feature design?*
  6. *Is the CVSS 3.1 score calculated using actual exploit metrics (AV:N/AC:L...)?*
  7. *Can the issue be reproduced with a minimal, copy-pasteable `curl` command?*
- If any question fails, abort submission and document failure reason.

#### 2.5 Report Synthesis & Submission Package
- Route to [`report-writing`](file:///.agents/skills/report-writing/SKILL.md) to generate the final report in `reports/REP-2026-XXX.md`.
- Formulate report using the **Impact-First Title & Statement**:
  - Format: `[Vulnerability Class] in [Endpoint/Function] leads to [Direct Concrete Impact]`
  - Include exact curl PoC, step-by-step reproduction, and defensive patch recommendation.

---

## 3. Safe Diagnostic Boundaries (Rules of Engagement)

All agents must strictly operate within established safe diagnostic boundaries:

| Boundary | Strict Rule |
| :--- | :--- |
| **No Denial of Service** | Strictly prohibited from executing volumetric load tests, low-and-slow DoS attacks, resource exhaustion, or unchecked concurrency. Max 5 concurrent requests during race condition testing. |
| **Two-Account Principle** | When testing access control (IDOR, privilege escalation), always use two researcher-owned test accounts (e.g., Tenant A = Victim, Tenant B = Attacker). Never access or manipulate real customer data. |
| **Zero Data Destruction** | Never execute `DELETE`, `DROP`, or state-destructive mutations on non-researcher accounts. Write tests must operate strictly on test data created during the session. |
| **Rate Throttling** | Limit automated scanning and API probing to maximum 5 requests/sec unless target policy specifies lower. |
| **Credential Safety** | Never commit, leak, or share real API keys, bearer tokens, or session secrets. Anonymize all PoC tokens as `<VICTIM_TOKEN>` and `<ATTACKER_TOKEN>`. |
| **Safe Harbor Adherence** | Only engage with programs that provide Safe Harbor protection, and adhere strictly to all program-specific exclusions. |

---

## 4. Skills Routing & Dispatch Directory

| Skill | Primary Trigger / Task | CLI / Usage Syntax |
| :--- | :--- | :--- |
| [`bb-methodology`](file:///.agents/skills/bb-methodology/SKILL.md) | Start of session, target phase routing, developer psychology analysis. | Review methodology phases 1-5 before recon. |
| [`agent-reach`](file:///.agents/skills/agent-reach/SKILL.md) | Search public HackerOne writeups, Git disclosures, CVEs, platform feeds. | Query target disclosures & past resolved reports. |
| [`security-bounty-hunter`](file:///.agents/skills/security-bounty-hunter/SKILL.md) | Remote reachable vulnerability hunting & attack surface mapping. | Execute remote vulnerability surface analysis. |
| [`bug-hunt-swarm`](file:///.agents/skills/bug-hunt-swarm/SKILL.md) | Multi-hypothesis root-cause exploration on anomalous responses. | Parallel read-only investigation across edge cases. |
| [`triage-validation`](file:///.agents/skills/triage-validation/SKILL.md) | Validation gate before writing report; CVSS 3.1 verification. | 7-Question Gate and Always-Rejected check. |
| [`report-writing`](file:///.agents/skills/report-writing/SKILL.md) | Formatting submission reports for H1 / Bugcrowd / Intigriti / Immunefi. | Impact-first report formatting & downgrade counter. |
| [`subagent-driven-development`](file:///.agents/skills/subagent-driven-development/SKILL.md) | Task breakdown, multi-subagent execution, and milestone verification. | Coordinate subagent worktrees and task plans. |

---

## 5. Knowledge Base & Analytics Lifecycle

Every finding lifecycle concludes with automated compilation:

1. **Resolution Capture:**
   - On reward:
     ```bash
     python scripts/index_manager.py new success KB-2026-XXX --title "..." --target "..."
     ```
   - On rejection / duplicate:
     ```bash
     python scripts/index_manager.py new failure KB-2026-XXX --title "..." --target "..."
     ```
2. **Repository Validation:**
   ```bash
   python scripts/index_manager.py validate
   ```
3. **Index Recompilation:**
   ```bash
   python scripts/index_manager.py reindex
   ```
4. **Performance Review:**
   ```bash
   python scripts/index_manager.py stats
   ```
