---
id: {{ID}}
title: "{{TITLE}}"
target: "{{TARGET}}"
platform: HackerOne
date: {{DATE}}
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
  - horizontal-privilege-escalation
lessons_learned:
  - "Inspect non-standard API sub-routes and background job exports for missing ownership checks."
  - "Clear, non-destructive PoC scripts drastically accelerate reward payout timelines."
---

# Success Post-Mortem: {{TITLE}}

## 1. Overview & Reward Metrics
- **Record Identifier:** {{ID}}
- **Target Organization:** {{TARGET}}
- **Platform:** HackerOne
- **Date Awarded:** {{DATE}}
- **Severity Assessed:** High
- **CVSS v3.1 Score:** 8.5
- **Bounty Awarded:** $3,000 USD
- **Vulnerability Class:** CWE-639: Broken Object Level Authorization (IDOR)
- **Root Cause Category:** Access Control

---

## 2. Technical Vulnerability Breakdown
The target platform exposed an invoice export microservice. While the primary invoice retrieval API (`/api/v1/invoices/:id`) properly checked user ownership against session claims, the asynchronous bulk export endpoint (`/api/v1/export/invoices`) accepted arbitrary list arrays of IDs without validating ownership against the current user's workspace ID.

### Proof of Concept
```http
POST /api/v1/export/invoices HTTP/1.1
Host: api.{{TARGET_DOMAIN}}
Authorization: Bearer <ATTACKER_TOKEN>
Content-Type: application/json

{
  "invoice_ids": ["inv_1001", "inv_1002", "inv_9999"],
  "format": "csv"
}
```

The system responded with HTTP 202 Accepted and delivered an S3 signed link containing records across unassociated accounts.

---

## 3. Timeline of Engagement
- **T0 (Discovery):** Identified export endpoint during proxy traffic analysis.
- **T+1h (Validation):** Verified cross-tenant leakage using two dedicated test accounts.
- **T+2h (Report Submitted):** Submitted complete PoC with curl command and CVSS calculation.
- **T+24h (Triaged):** Triaged by security team as High Severity.
- **T+72h (Resolved & Paid):** Fix deployed; $3,000 bounty awarded.

---

## 4. Why This Finding Succeeded
1. **Targeting Asynchronous / Secondary Flows:** Many hunters only test primary CRUD routes; export workers often rely on trusted internal messaging queues that lack tenant contexts.
2. **Deterministic PoC:** Providing two test accounts demonstrated zero ambiguity and no risk of business disruption.
3. **Aligned Severity Justification:** Documented horizontal tenant data exposure directly matching program payout criteria.

---

## 5. Tactical Takeaways & Methodology Refinements
- Always check export, PDF render, report generation, and batch operation endpoints.
- Automate detection of batch operations where request array items are processed sequentially without scoped database queries.
