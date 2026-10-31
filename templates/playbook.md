---
id: {{ID}}
title: "{{TITLE}}"
target: "{{TARGET}}"
platform: {{PLATFORM}}
date: {{DATE}}
type: playbook
status: Hunting
severity: High
cvss_score: null
bounty_payout: 0
vuln_class: "N/A"
root_cause_category: "N/A"
failure_reason: null
techniques:
  - parameter-tampering
  - logic-probing
lessons_learned:
  - "Document repeatable attack surface discovery workflows."
  - "Catalog bypass patterns for common authorization and input validation defenses."
---

# Tactical Playbook: {{TITLE}}

## 1. Vulnerability Overview & CWE Mechanics
- **Vulnerability Class:** {{TITLE}}
- **Target Context:** {{TARGET}}
- **Default Severity:** High
- **Root Cause Category:** Access Control / Business Logic

---

## 2. Attack Surface Discovery & Recon
1. Map out target endpoints handling multi-tenant identifiers or permission flags.
2. Filter for auxiliary and batch routes (exports, bulk updates, background processing).

---

## 3. Test Vectors & Bypass Patterns
- **Vector 1: Direct Resource ID Swapping**
  - Replace tenant/object IDs with target user/tenant identifiers across GET and POST parameters.
- **Vector 2: Request Structure Manipulation**
  - Wrap scalar fields in arrays or nested JSON objects to bypass superficial property checks.

---

## 4. Remediation & Hardening Guidelines
- Enforce authoritative backend authorization checks against the authenticated session context.
- Never trust client-supplied tenant, role, or object ownership parameters.
