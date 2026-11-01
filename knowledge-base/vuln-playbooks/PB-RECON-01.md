---
id: PB-RECON-01
title: "Continuous Automated Recon & Attack Surface Monitoring"
target: "Global"
platform: Other
date: 2026-10-31
type: playbook
status: Hunting
severity: High
cvss_score: null
bounty_payout: 0
vuln_class: "N/A"
root_cause_category: "Configuration"
failure_reason: null
techniques:
  - asset-discovery
  - tech-stack-fingerprinting
  - api-surface-mapping
lessons_learned:
  - "Automation replaces repetitive busywork; hackers win bug bounties by catching new and untested assets first."
  - "Never run full port scans on hundreds of hosts upfront; use smart two-tiered scanning (top 1000 first, full ports only on anomalies)."
  - "Visual recon via automated screenshots enables spotting internal portals and staging APIs in seconds instead of hours."
---

# Tactical Playbook: Continuous Automated Recon & Attack Surface Monitoring

## 1. Core Philosophy & The 3 Automated Pillars
Most bug bounty researchers waste 80% of their operational time performing manual, repetitive tasks: running tools one-off, manually pinging dead hosts, and clicking through subdomains individually. In modern bug bounty programs with hundreds of competing hackers, speed and asset delta detection determine success.

This methodology automates the entire discovery, scanning, and visual inspection workflow into a continuous 24/7 pipeline:

```
[Target Wildcard: *.target.com]
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. SUBDOMAIN DISCOVERY & CONTINUOUS MONITORING              │
│    - Multi-Source Aggregation: subfinder + amass + crt.sh   │
│    - Daily Diff Engine: diff(Today, Yesterday)              │
│    - Instant Alerting on New/Untested Assets                │
└────────────────────────┬────────────────────────────────────┘
                         │ (Alive Hosts Only)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SMART TIERED PORT SCANNING & VULNERABILITY AUDITING      │
│    - Fast Liveness Pre-filter via httpx                     │
│    - Tier 1: Fast Top 1000 Port Scan (~2 min/host)         │
│    - Tier 2: Deep 1-65535 Scan (Anomalous Ports: 8080/8443) │
│    - Automated Known CVE & Config Audit via Nuclei          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. VISUAL RECON & TECH STACK PROFILING                      │
│    - Headless Browser Automated Screenshots (EyeWitness)    │
│    - Rapid Visual Gallery Triage (Spot Staging / Admin UI)  │
│    - Tech Stack Fingerprinting (Wappalyzer / Headers)       │
│    - Target Matching to High-Probability Bug Classes        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Pillar 1: Subdomain Discovery & Diff Monitoring

### Multi-Source Aggregation
Never rely on a single enumeration tool. Combine passive certificate logs, API aggregators, and DNS query engines:
- **ProjectDiscovery Subfinder:** Rapid passive DNS enumeration.
- **OWASP Amass:** Active and passive network mapping.
- **Assetfinder & crt.sh:** Certificate Transparency log scraping.

### Continuous 24/7 Monitoring & Diffing
Running discovery once per week guarantees finding already picked-over targets. Run automated discovery every 24 hours:

```bash
# 1. Aggregate fresh assets
subfinder -d target.com -silent > today.txt
assetfinder --subs-only target.com >> today.txt
sort -u today.txt -o today_sorted.txt

# 2. Compute the Delta (New Assets Launched in Last 24h)
comm -13 yesterday_sorted.txt today_sorted.txt > new_assets.txt

# 3. Alert immediately on newly detected assets
if [ -s new_assets.txt ]; then
    echo "[!] NEW ASSET DETECTED - Untested attack surface:"
    cat new_assets.txt
    # Send notification hook (Slack/Discord/Telegram)
fi

# 4. Rotate baseline
mv today_sorted.txt yesterday_sorted.txt
```

> **Why this wins bounties:** New assets launched by development teams represent fresh, untested attack surfaces that have not yet undergone security audits.

---

## 3. Pillar 2: Smart Tiered Port Scanning & Vulnerability Probing

### Step 2.1: Pre-Filter with Liveness Checking
Never scan unresolvable or dead hostnames with port scanners. Filter the aggregated list through `httpx`:

```bash
httpx -l new_assets.txt -silent -status-code -title -tech-detect -o alive_hosts.txt
```

### Step 2.2: Smart Two-Tiered Port Scanning (Fast vs Brute Force)
Full port scans (ports 1–65535) across hundreds of hosts are slow, noisy, and trigger firewall rate limits. Adopt a two-tier strategy:

1. **Tier 1 (Rapid Top 1000 Scan):**  
   Scan the top 1000 common TCP ports (`nmap -T4 --top-ports 1000`). Takes ~2 minutes per host instead of 20 minutes.
2. **Tier 2 (Deep Full Scan on Anomalies):**  
   If Tier 1 reveals unusual listening ports (e.g., `8080`, `8443`, `8000`, `9000`, `5000`, `3000`), trigger a full 1–65535 scan exclusively against that specific host.

### Step 2.3: Automated Known Vulnerability Detection
Run targeted vulnerability scans on live services using `nuclei` with curated templates:
- Exposed `.git` repositories and `.env` credentials.
- Publicly accessible Swagger / OpenAPI specification files.
- Known CVEs for identified service versions.

```bash
nuclei -l alive_hosts.txt -t cves/ -t exposures/ -t misconfiguration/ -severity medium,high,critical -o nuclei_findings.txt
```

---

## 4. Pillar 3: Visual Recon & Tech Stack Profiling

### Automated Headless Screenshotting
Port scan text output fails to convey application context. Screenshots allow a researcher to visually inspect hundreds of web interfaces in minutes:
- Utilize headless browser automation (`EyeWitness`, `gowitness`, or custom Chrome headless scripts).
- Generate a unified HTML gallery sorting sites by response code and visual similarities.

### High-Value Visual Signatures to Flag Instantly:
| Visual Signature | Priority | Target Flaw Class |
| :--- | :--- | :--- |
| **Admin / Dashboard Login Panels** | Critical | Default creds, auth bypass, brute-force |
| **API Documentation (Swagger / Redoc)** | High | IDOR, unauthenticated endpoints, BOLA |
| **Directory Indexing / File Listing** | High | Source code disclosure, backup file download |
| **Staging / Dev / QA Splash Banners** | Critical | Hardcoded debug credentials, test data leaks |
| **Error / Stack Trace Pages (Laravel / Django)** | Medium | Sensitive path disclosure, debug mode enabled |

### Tech Stack Identification & Specialized Attack Routing
Profile the underlying technologies using Wappalyzer, BuiltWith, or response headers:
- **WordPress detected:** Check `/wp-json/`, enumerate plugins, audit REST API user routes (`/wp-json/wp/v2/users`).
- **Spring Boot / Java detected:** Probe `/actuator`, `/actuator/env`, `/actuator/heapdump`, Jolokia.
- **Node.js / Express detected:** Test for prototype pollution, SSRF via image parsers.
- **Modern SPA (React / Angular / Vue):** Download and audit webpack source maps, JavaScript bundles, and API route definitions for unlinked endpoints and sensitive client-side keys.

---

## 5. Real-World Case Study: $5,000 IDOR via Staging Asset Alert

1. **Detection:** The daily continuous monitoring script detected a new subdomain: `staging-api.target.com`.
2. **Visual Recon:** Automated screenshot revealed an unauthenticated Swagger UI documentation page left publicly accessible on the staging host.
3. **Exploitation:** The Swagger docs exposed a user details endpoint (`GET /api/v1/users/{id}`). Testing ID substitution demonstrated zero tenant authorization checks.
4. **Outcome:** Full PII and customer record disclosure reported to the program; awarded a $5,000 Critical severity bounty.

Without automated continuous monitoring and visual screenshotting, the newly deployed staging asset would have either been missed entirely or discovered by competing researchers days later.
