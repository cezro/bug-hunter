---
id: {{ID}}
title: "{{TITLE}}"
target: "{{TARGET}}"
platform: Bugcrowd
date: {{DATE}}
type: failure
status: Duplicate
severity: Medium
cvss_score: 5.3
bounty_payout: 0
vuln_class: "CWE-362: Race Condition"
root_cause_category: Race Condition
failure_reason: Duplicate (Speed)
techniques:
  - parallel-requests
  - limit-overrun
lessons_learned:
  - "High-traffic promotional coupon endpoints on public programs are saturated within hours."
  - "Shift focus from shallow coupon races to complex state machines and multi-step workflows."
---

# Failure Post-Mortem: {{TITLE}}

## 1. Finding Overview & Rejection Classification
- **Record Identifier:** {{ID}}
- **Target Organization:** {{TARGET}}
- **Platform:** Bugcrowd
- **Submission Date:** {{DATE}}
- **Assessed Severity:** Medium
- **CVSS v3.1 Score:** 5.3
- **Outcome Status:** Duplicate
- **Failure Reason:** Duplicate (Speed)
- **Vulnerability Class:** CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization

---

## 2. Technical Vulnerability Context
The target application featured a coupon redemption endpoint (`POST /api/v1/promotions/apply`) that lacked database transaction locking or atomic decrement operations. Sending 25 concurrent requests via HTTP/2 single-packet multiplexing allowed applying a single-use $20 discount code multiple times.

---

## 3. Post-Mortem & Root Cause of Failure
### Why Was This Duplicate / Rejected?
- **Timeline Disadvantage:** The promotion had been announced on target marketing channels 48 hours prior. A fellow researcher submitted the exact same race condition 14 hours ahead of our report.
- **Low Barrier to Entry:** Automated race condition scanners readily flag promo redemption endpoints.
- **Surface Depth:** The vulnerability was on the outermost, most visible marketing surface of the application.

---

## 4. Tactical Mistakes & Blindspots
1. Spending recon time on publicized, top-of-funnel marketing campaigns rather than complex authenticated enterprise workflows.
2. Relying on manual testing instead of immediate scripted verification when high-traffic features are deployed.

---

## 5. Preventative Actions & Methodology Refinement
- **Rule 1:** When public marketing features launch, do not invest more than 30 minutes unless deep business logic chaining is uncovered.
- **Rule 2:** Prioritize race conditions on complex financial ledger operations, balance withdrawals, and asynchronous reconciliation jobs over simple checkout discounts.
- **Rule 3:** Update triage checklist to evaluate public discovery recency before investing report preparation time.
