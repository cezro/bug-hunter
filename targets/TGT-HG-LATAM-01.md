---
id: TGT-HG-LATAM-01
title: "HostGator LATAM Profile"
target: "HostGator LATAM"
platform: Bugcrowd
date: 2026-10-31
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
  - ai-agent-auditing
  - api-surface-mapping
lessons_learned:
  - "Target has newly prioritized AI Agents and AI-driven VPS features."
  - "carrinho.hostgator.com.br is explicitly out of scope per brief update."
---

# Target Profile: HostGator LATAM

## 1. Program Summary & Safe Harbor
- **Platform:** Bugcrowd
- **Engagement URL:** https://bugcrowd.com/engagements/hostgator-latam-bb
- **Safe Harbor Status:** Standard Safe Harbor (CFAA/DMCA exemption for good-faith testing)
- **Organization:** Newfold Digital (HostGator LATAM)
- **Email Tagging:** Researcher `@bugcrowdninja.com` email address required for signups.
- **Testing Constraints:** 
  - Do NOT create multiple accounts for testing within HostGator LATAM.
  - No automated high-frequency rate-limit testing / DoS.
  - No testing of customer-controlled hosting environments.

---

## 2. In-Scope Assets & Scope Boundaries
### In-Scope (Strict Boundaries)
- `www.hostgator.com.br/` / `https://www.hostgator.com.br/` (MySQL, Go, ReactJS)
- `https://financeiro.hostgator.com.br` (Go, ReactJS, PHP)
- **Subdomain flows:** Any subdomain flows (able to clearly showcase navigation flow) after user authentication to the targets above.
- **Priority Focus Areas (Explicit Program Announcements):**
  - **AI Agents Section**
  - **VPS Features, specifically AI-related functionality** (AI tools to streamline server management and automation)

### Out-of-Scope (Strict Exclusions)
- `https://carrinho.hostgator.com.br/` (Recently explicitly removed from scope)
- Subdomains that are HostGator customer-controlled environments (shared/VPS user cPanel/sites)
- `academy.hostgator.com`, `*.hostgator.mx` (non-bounty VDP only)
- Third-party assets
- Chatboxes on applications (general unauthenticated chat widgets)
- DoS/DDoS, missing rate limits, anti-automation
- Missing security headers, DMARC, SPF, SSL/TLS ciphers
- Open redirects, clickjacking, self-XSS, verbose error messages, stack traces
- OAuth session token not invalidated on logout

---

## 3. Technology Stack & Infrastructure Fingerprint
- **Edge / CDN:** Cloudflare Enterprise / CDN
- **Backend Languages/Frameworks:** Go microservices, PHP (legacy billing portal integration), Node.js / ReactJS
- **Identity & Auth:** Centralized SSO / Newfold Digital Auth (`financeiro.hostgator.com.br`)
- **AI Infrastructure:** Newfold Digital AI Services Gateway (`api-gw.builderservices.io` / HostGator AI Agent microservices)
- **Database:** MySQL

---

## 4. Key Business Logic & High-Value Attack Surfaces
1. **AI Agents Section:**
   - AI agent orchestration, model routing, system prompt extraction, indirect prompt injection.
   - Centralized LLM gateway auth: checking for enterprise token theft, arbitrary model switching (GPT-4o/Claude), quota abuse.
2. **AI-driven VPS Management:**
   - Automated server management commands, AI shell execution, command injection / prompt-to-command traps.
   - Privilege escalation via server control APIs.
3. **Financeiro / Billing Portal (`financeiro.hostgator.com.br`):**
   - Invoices, subscription management, customer data APIs (IDOR / BOLA on invoice IDs, VPS client IDs).
   - SSO token transfer between marketing site and billing portal.

---

## 5. Active Hunting Objectives & Progress
- [ ] Subdomain discovery & port scanning on `hostgator.com.br` (Pillars 1 & 2)
- [ ] Discover endpoints and APIs for the AI Agents Section and AI-driven VPS features
- [ ] Run HexStrike AI Tactical Decision Engine on Go/PHP/React/AI stack
- [ ] Deploy Dialectic Swarm (Prover vs Disprover) to analyze AI agent endpoints and financeiro APIs
- [ ] Enforce 7-Question Gate and validate findings before reporting
