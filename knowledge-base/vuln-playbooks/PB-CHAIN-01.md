---
id: PB-CHAIN-01
title: "Multi-Stage Attack Chain Correlation & Vulnerability Prioritization"
target: "Global"
platform: Other
date: 2026-10-31
type: playbook
status: Hunting
severity: High
cvss_score: null
bounty_payout: 0
vuln_class: "N/A"
root_cause_category: "Business Logic"
failure_reason: null
techniques:
  - parameter-tampering
  - auth-context-switching
  - ai-gateway-abuse
lessons_learned:
  - "Isolated Medium findings often get closed as informative; chaining two Medium findings into an end-to-end exploit unlocks High/Critical bounties."
  - "Always tailor tooling and probing parameters to the detected technology stack rather than firing generic payloads."
  - "Enforce adaptive timing profiles (e.g., Conservative/Stealth) when Cloudflare or Akamai is detected to prevent IP bans."
---

# Tactical Playbook: Multi-Stage Attack Chain Correlation & Vulnerability Prioritization (HexStrike Architecture)

## 1. HexStrike 10-Tier Vulnerability Priority Matrix
Rather than probing targets randomly, high-performing hunters organize test efforts according to an impact-weighted hierarchy:

| Priority | Vulnerability Class | Default Severity | Core Test Vectors |
| :---: | :--- | :---: | :--- |
| **10** | **Remote Code Execution (RCE)** | Critical | SSTI, Command Injection, Deserialization, Malicious File Upload |
| **9** | **SQL Injection (SQLi)** | Critical | Error-based, Boolean Blind, Time-based, Stacked Queries |
| **8** | **IDOR / BOLA** | High | Numeric ID decrement, UUID swapping, JSON body parameter tampering |
| **8** | **Server-Side Request Forgery (SSRF)** | High | Cloud metadata (`169.254.169.254`), Internal Gateway APIs, Webhook sinks |
| **8** | **AI Gateway Abuse & Quota Drainage** | High | Deployment tampering (`gpt-4o`/`o1`), System prompt bypass, Tool injection |
| **8** | **Authentication / Session Bypass** | High | OAuth redirect leaks, JWT `alg:none`/key confusion, Pre-auth leaks |
| **7** | **XML External Entity (XXE)** | High | SAML assertions, SVG parsers, SOAP/XML endpoints |
| **7** | **Race Conditions** | High | Limit-overruns (coupons, gift cards, balances), TOCTOU state floods |
| **6** | **Credentialed CORS Misconfiguration** | Med-High | Dynamic subdomain reflection with `Access-Control-Allow-Credentials: true` |
| **6** | **Stored XSS (Privileged Context)** | Medium | Admin dashboards, order review notes, tenant profile fields |

---

## 2. Technology-Driven Attack Surface Mapping
HexStrike's core innovation is **dynamic attack tailoring**: the target's detected software stack determines the immediate test playbook.

```
┌─────────────────────────────────┐      ┌───────────────────────────────────────────────┐
│ Detected Technology             │ ───► │ Immediate High-Yield Test Vectors             │
├─────────────────────────────────┤      ├───────────────────────────────────────────────┤
│ WordPress / WVC Themes          │ ───► │ REST API user routes (/wp-json/wp/v2/users),  │
│                                 │      │ custom plugin endpoints, unauthenticated auth │
├─────────────────────────────────┤      ├───────────────────────────────────────────────┤
│ Central AI Gateway / Azure OAI  │ ───► │ Client-controlled model deployment parameters,│
│                                 │      │ enterprise quota abuse, citation leaks        │
├─────────────────────────────────┤      ├───────────────────────────────────────────────┤
│ Multi-Tenant User Subdomains    │ ───► │ CORS reflection, CNAME takeover, token theft  │
│ (*.target.com)                  │      │ across shared wildcard cookies                │
├─────────────────────────────────┤      ├───────────────────────────────────────────────┤
│ React / Microfrontend Bundles   │ ───► │ Unminified source maps, unlinked admin APIs,  │
│                                 │      │ hardcoded API keys in SystemJS manifests      │
└─────────────────────────────────┘      └───────────────────────────────────────────────┘
```

---

## 3. Attack Chain Correlation: Turning Mediums into Criticals
Individual anomalies that might otherwise be triaged as Low or Informative can be chained to demonstrate catastrophic business impact:

### Chain Pattern 1: User Subdomain CORS $\rightarrow$ Bearer Token Theft $\rightarrow$ AI Gateway Quota Drain
1. **Anomaly A (Medium):** `app-gateway.web.com` reflects any `*.web.com` origin with `Access-Control-Allow-Credentials: true`.
2. **Anomaly B (Medium):** Any user can publish custom HTML/JavaScript on a free trial subdomain.
3. **Anomaly C (High):** `api-gw.builderservices.io/ai-api/v3.0/chat` allows executing prompts against enterprise `gpt-4o` using any valid Bearer JWT.
4. **The Critical Chain:**
   - Attacker deploys malicious script on `attacker-site.web.com`.
   - Victim visits attacker's site while logged into Bluehost/Web.com.
   - Script performs cross-origin preauth call to `app-gateway.web.com` to steal `X-CSRF-TOKEN` and JWT Bearer token.
   - Attacker uses the stolen token to exhaust Newfold's enterprise Azure OpenAI compute allocations.

### Chain Pattern 2: Information Disclosure $\rightarrow$ SSRF $\rightarrow$ Internal Admin Access
1. **Anomaly A:** API response error leaks internal microservice hostnames (`http://billing-internal.local`).
2. **Anomaly B:** Profile image upload accepts external URL.
3. **The Chain:** Supply internal URL to image processor to reach unauthenticated admin management endpoints behind the firewall.

---

## 4. Adaptive Timing Profiles for Safe WAF Evasion
To avoid triggering automated WAF IP blocks (Cloudflare, Akamai, Imperva), testing scripts must dynamically adjust their concurrency and delay profiles:

| Profile | Delay / Request | Max Concurrency | Request Timeout | Trigger Condition |
| :--- | :---: | :---: | :---: | :--- |
| **Aggressive** | 0.1s | 20 | 5s | Direct IP access, zero WAF, local test container |
| **Normal** | 0.5s | 10 | 10s | Standard target with basic rate limiting |
| **Conservative** | 1.5s | 3 | 15s | Cloudflare / Akamai present; prevents IP blocks |
| **Stealth** | 3.0s | 1 | 25s | Strict CAPTCHA / Bot management mitigation active |

Execute the assessment plan via:
```bash
python scripts/hexstrike_decision.py <target_domain> --tech <stack>
```
