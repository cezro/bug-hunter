import re

path = r"c:\Users\Zero\Documents\GitHub Repositories\bug-hunter\AGENTS.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """#### 2.2 Safe Surface Mapping & Fingerprinting
- Route to [`security-bounty-hunter`](file:///.agents/skills/security-bounty-hunter/SKILL.md) and [`bb-methodology`](file:///.agents/skills/bb-methodology/SKILL.md) for passive/active fingerprinting:
  - WAF / Edge CDN (Cloudflare, AWS CloudFront, Fastly, Akamai).
  - API architecture (REST, GraphQL, gRPC, WebSocket).
  - Auth mechanisms (OAuth2/OIDC, JWT RS256/HS256, SAML, session cookies).
- Record findings into `targets/TGT-<ID>.md`."""

replacement = """#### 2.2 Continuous 3-Pillar Recon & Surface Mapping (CyberFlow Methodology)
- Route to [`security-bounty-hunter`](file:///.agents/skills/security-bounty-hunter/SKILL.md), [`bb-methodology`](file:///.agents/skills/bb-methodology/SKILL.md), and playbook [`PB-RECON-01`](file:///c:/Users/Zero/Documents/GitHub%20Repositories/bug-hunter/knowledge-base/vuln-playbooks/PB-RECON-01.md):
  1. **Subdomain Discovery & 24/7 Delta Monitoring:**
     - Multi-source aggregation (`subfinder`, `amass`, `assetfinder`, `crt.sh`).
     - Daily baseline diffing: `diff(today, yesterday)` to instantly flag new, untested assets (highest probability of bugs).
  2. **Smart Tiered Port Scanning & Liveness Pre-Filtering:**
     - Pre-filter alive hosts with `httpx` (never scan dead hosts).
     - Tier 1: Fast top 1000 ports (~2 min/host).
     - Tier 2: Deep 1-65535 scan exclusively on anomalous listening ports (8080, 8443, 8000, 9000).
     - Automated vulnerability auditing using `nuclei` templates (exposed Git, Swagger/OpenAPI docs, unpatched CVEs).
  3. **Visual Recon & Tech Stack Profiling:**
     - Headless automated screenshot gallery (`EyeWitness` / `scripts/recon_pipeline.py`).
     - Rapid visual triage: identify admin portals, unauthenticated staging APIs, and directory listings in seconds.
     - Tech stack profiling (Wappalyzer / header analysis) to match targets to optimal vulnerability classes.
- Record findings into `targets/TGT-<ID>.md`. Execute via:
  ```bash
  python scripts/recon_pipeline.py <domain> --slug <SLUG>
  ```"""

if target in text:
    text = text.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("[+] Successfully updated AGENTS.md!")
else:
    print("[-] Target not found in AGENTS.md")
