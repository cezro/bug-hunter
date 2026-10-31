---
id: TGT-ACME-01
title: "Acme Cloud Services Target Profile"
target: "Acme Cloud Services"
platform: HackerOne
date: 2026-03-01
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
  - "Billing and background export queues have historically contained tenant authorization flaws."
---

# Target Profile: Acme Cloud Services

## 1. Scope & Safe Harbor
- **Platform:** HackerOne (`https://hackerone.com/acme-cloud`)
- **Safe Harbor:** Gold Standard (Full Safe Harbor)
- **Primary Domain:** `*.acmecloud.io`
- **Key API Target:** `api.acmecloud.io`

## 2. Tech Stack
- **Gateway:** Kong API Gateway + Cloudflare
- **Backend:** Python FastAPI, Celery background workers
- **Database:** PostgreSQL with row-level security (RLS) on primary tables, Redis queue

## 3. Threat Matrix & Focus Areas
- Focus on asynchronous Celery jobs which occasionally lack session claims.
- Monitor `/api/v2/organizations/*/exports` and invoice management.
