---
id: {{ID}}
title: "{{TITLE}}"
target: "{{TARGET}}"
platform: {{PLATFORM}}
date: {{DATE}}
type: report
status: In-Triage
severity: High
cvss_score: 8.5
bounty_payout: 0
vuln_class: "CWE-639: IDOR"
root_cause_category: Access Control
failure_reason: null
techniques:
  - parameter-tampering
  - horizontal-privilege-escalation
lessons_learned:
  - "Highlight concrete business impact and clear reproduction steps to ensure rapid triage."
---

# Vulnerability Report: {{TITLE}}

## Executive Summary
A Broken Object Level Authorization (IDOR) vulnerability was identified in the `{{TARGET}}` application. An authenticated attacker can access or manipulate sensitive resources belonging to other tenants by tampering with the resource identifier parameter in API requests.

---

## Vulnerability Details
- **Vulnerability Class:** CWE-639: Authorization Bypass Through User-Controlled Key
- **Root Cause Category:** Access Control
- **Affected Endpoint:** `GET https://api.{{TARGET_DOMAIN}}/v2/workspaces/{workspace_id}/invoices/{invoice_id}`
- **CVSS v3.1 Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` (Base Score: 8.5)

---

## Step-by-Step Proof of Concept (PoC)

### Prerequisites
1. Attacker Account (Tenant B): `attacker@tenant-b.com`
2. Victim Account (Tenant A): `victim@tenant-a.com` with invoice `inv_999`

### Reproduction Steps
1. Log in to the application using Tenant B credentials and obtain an active session token.
2. Send the following HTTP request substituting `inv_999` (an invoice created by Tenant A):

```bash
curl -X GET "https://api.{{TARGET_DOMAIN}}/v2/workspaces/ws_222/invoices/inv_999" \
  -H "Authorization: Bearer <TOKEN_TENANT_B>" \
  -H "Accept: application/json"
```

3. **Observed Result:**  
   The API responds with HTTP 200 OK containing full financial and personally identifiable information (PII) of Tenant A.

4. **Expected Result:**  
   The API must respond with HTTP 403 Forbidden or HTTP 404 Not Found, enforcing strict tenant boundary validation.

---

## Business Impact
An attacker can enumerate and dump all organizational financial records, client names, transaction totals, and payment metadata across the platform without restriction.

---

## Suggested Remediation
Implement strict authorization checks in the controller layer verifying that the authenticated user's organization context matches the owning tenant of the requested object before fetching:

```python
# Remediation Pattern
invoice = Invoice.query.filter_by(id=invoice_id, workspace_id=current_user.workspace_id).first_or_404()
```
