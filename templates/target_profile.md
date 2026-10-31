---
id: {{ID}}
title: "{{TITLE}}"
target: "{{TARGET}}"
platform: {{PLATFORM}}
date: {{DATE}}
type: target_profile
status: Hunting
severity: None
cvss_score: null
bounty_payout: 0
vuln_class: "N/A"
root_cause_category: "N/A"
failure_reason: null
techniques:
  - asset-discovery
  - tech-stack-fingerprinting
  - api-surface-mapping
lessons_learned:
  - "Map out microservice routing before deep logic probing."
---

# Target Profile: {{TARGET}}

## 1. Program Summary & Safe Harbor
- **Platform:** {{PLATFORM}}
- **Program Type:** Public / Private Bug Bounty
- **Safe Harbor Status:** Full Safe Harbor (Gold Standard)
- **Policy URL:** https://hackerone.com/{{TARGET_SLUG}}
- **Bounty Table:**
  - Critical: $5,000 - $15,000
  - High: $2,000 - $5,000
  - Medium: $500 - $2,000
  - Low: $100 - $500

---

## 2. In-Scope Assets & Scope Boundaries
### In-Scope (Strict Boundaries)
- `*.{{TARGET_DOMAIN}}`
- `api.{{TARGET_DOMAIN}}`
- Mobile Apps: Android / iOS (Package: `com.{{TARGET_SLUG}}.app`)

### Out-of-Scope (Forbidden)
- Third-party SaaS (`zendesk.com`, `statuspage.io`, etc.)
- DoS, DDoS, automated high-frequency brute-forcing
- Social engineering, phishing, physical testing
- Leakage of employee PII or destructive data manipulation

---

## 3. Technology Stack & Infrastructure Fingerprint
- **Cloud Infrastructure:** AWS (CloudFront, S3, ALB, ECS)
- **Edge / WAF:** Cloudflare Enterprise
- **API Architecture:** REST (v1/v2), GraphQL (`/graphql`)
- **Authentication & Identity:** OAuth 2.0 / OIDC, JWT Bearer tokens with RS256
- **Frontend Framework:** Next.js (React)
- **Backend Languages/Frameworks:** Node.js / Express, Python / Django, Go microservices
- **Database Systems:** PostgreSQL, Redis

---

## 4. Key Business Logic & High-Value Attack Surfaces
1. **Multi-Tenant Organizations & RBAC:**
   - Roles: Owner, Admin, Member, Billing Manager, Read-Only Guest
   - Cross-tenant data isolation mechanisms
2. **Billing & Subscriptions:**
   - Stripe Webhook handlers, seat adjustments, upgrade/downgrade logic
3. **File Processing & Exports:**
   - CSV / PDF export jobs, asynchronous Celery workers, S3 presigned URLs
4. **Third-Party Integrations:**
   - GitHub / Slack OAuth app webhooks, custom webhook dispatchers

---

## 5. Historical Intelligence & Disclosed Vulnerabilities
- Past disclosure: IDOR in user invite endpoints (CWE-639)
- Common developer pattern: UUIDv4 used on primary endpoints, but legacy sequential IDs accepted by internal API routes.

---

## 6. Active Hunting Objectives & Progress
- [ ] Map out all unauthenticated REST endpoints exposed under `/api/v1/`
- [ ] Inspect GraphQL introspection schema for undocumented admin mutations
- [ ] Test cross-tenant access controls on `/export` asynchronous jobs
