---
id: PB-IDOR-01
title: "Broken Object Level Authorization (IDOR) Tactical Playbook"
target: "Universal Web Applications"
platform: Other
date: 2026-03-01
type: playbook
status: Hunting
severity: High
cvss_score: null
bounty_payout: 0
vuln_class: "CWE-639: IDOR"
root_cause_category: Access Control
failure_reason: null
techniques:
  - parameter-tampering
  - horizontal-privilege-escalation
  - vertical-privilege-escalation
  - uuid-prediction
  - api-enumeration
lessons_learned:
  - "Target secondary actions (export, print, sync, restore) rather than primary CRUD routes."
  - "Test parameter wrapping: arrays, nested JSON, and query string overrides on POST requests."
---

# Tactical Playbook: Broken Object Level Authorization (IDOR / BOLA)

## 1. Overview & Threat Model
Broken Object Level Authorization occurs when an application receives user-supplied input to retrieve or manipulate an internal object without verifying that the requesting identity possesses authorized ownership or permission for that specific object.

- **CWE Classification:** CWE-639: Authorization Bypass Through User-Controlled Key
- **OWASP Category:** API1:2023 - Broken Object Level Authorization
- **Typical Severity:** High (8.0 - 8.8) to Critical (9.0+)

---

## 2. Attack Surface Discovery

### High-Yield Target Areas
1. **Secondary Lifecycle Operations:**
   - Soft-delete restore endpoints (`POST /api/items/{id}/restore`)
   - Bulk exports & report generation (`POST /api/reports/export`, `GET /export?ids=...`)
   - Document rendering (`GET /api/documents/{id}/render.pdf`)
   - Cloned / Duplicated entities (`POST /api/templates/{id}/duplicate`)
2. **Asynchronous / Background Workers:**
   - Batch job poll endpoints (`GET /jobs/{job_id}/results`)
   - Webhook retry triggers (`POST /webhooks/{webhook_id}/re-deliver`)
3. **Multi-Tenant Collaboration Features:**
   - Member invitation links, role assignments, workspace switching
   - Audit logs (`GET /api/organizations/{org_id}/audit-logs`)

---

## 3. Parameter Manipulation & Bypass Patterns

### Pattern A: Parameter Wrapping & Array Injection
When an API expects a scalar ID, pass a JSON array or object to bypass strict equality filters:
```http
POST /api/v1/invoices/cancel HTTP/1.1
Host: target.com
Content-Type: application/json

{"invoice_id": ["inv_123", "inv_victim_456"]}
```

### Pattern B: Method & Path Overrides
If `GET /api/users/victim_id` yields `403 Forbidden`, test:
- `POST /api/users/victim_id` with `X-HTTP-Method-Override: GET`
- `GET /api/users;victim_id` or `/api/users/./victim_id`
- Adding extensions: `/api/users/victim_id.json`

### Pattern C: Query Parameter Collision on POST Requests
Some gateways parse route parameters from the URL while internal microservices parse the body:
```http
POST /api/v1/workspaces/attacker_ws/settings?workspace_id=victim_ws HTTP/1.1
Host: target.com
Content-Type: application/json

{"workspace_id": "victim_ws", "allow_public_access": true}
```

### Pattern D: UUID Guessability & Historical Leakage
If identifiers use UUIDv4:
1. Search public JavaScript source maps or bundle files for hardcoded UUIDs.
2. Check public APIs (user profile, reviews, public organization directories) for exposed victim UUIDs.
3. Test if UUIDv1 (timestamp-based) is used instead of cryptographically random UUIDv4.

---

## 4. Triage & Verification Gate

Before submitting any IDOR report, verify against the **7-Question Gate**:
1. Is the exposed data actually private, or is it public tenant data?
2. Did you test with **two distinct user accounts** (Attacker & Victim)?
3. Can the vulnerability be reproduced cleanly via `curl` with sanitized tokens?
4. Is there actual sensitive data exposure or business logic degradation?
5. Does the finding adhere to safe testing policies (no data destruction or bulk dumping)?
