path = r"c:\Users\Zero\Documents\GitHub Repositories\bug-hunter\AGENTS.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """#### 2.3 Swarm Root-Cause Exploration & Anomaly Detection
- When an anomalous behavior or potential flaw is detected, route to [`bug-hunt-swarm`](file:///.agents/skills/bug-hunt-swarm/SKILL.md).
- Scaffold an investigation note:
  ```bash
  python scripts/index_manager.py new investigation INV-2026-XXX --title "<Hypothesis Title>" --target "<Target>"
  ```
- Swarm agents independently investigate hypotheses:
  - Agent A: Access control boundary checks (IDOR, role escalation).
  - Agent B: Input sanitation & logic flow (SSRF, business logic flaws).
  - Agent C: Race conditions & state synchronization."""

replacement = """#### 2.3 Swarm Root-Cause Exploration & Attack Chain Discovery (HexStrike AI Methodology)
- When anomalous behavior or target fingerprints are detected, run the HexStrike Tactical Decision Engine:
  ```bash
  python scripts/hexstrike_decision.py <domain> --tech <STACK>
  ```
- Route to [`bug-hunt-swarm`](file:///.agents/skills/bug-hunt-swarm/SKILL.md) and playbook [`PB-CHAIN-01`](file:///c:/Users/Zero/Documents/GitHub%20Repositories/bug-hunter/knowledge-base/vuln-playbooks/PB-CHAIN-01.md):
- Scaffold an investigation note:
  ```bash
  python scripts/index_manager.py new investigation INV-2026-XXX --title "<Hypothesis Title>" --target "<Target>"
  ```
- Swarm agents independently investigate and correlate findings according to the **HexStrike 10-Tier Priority Hierarchy**:
  - **Tier 10-9 (Critical):** RCE (SSTI, deserialization) & SQLi.
  - **Tier 8 (High):** IDOR/BOLA, SSRF, AI Gateway Abuse (arbitrary model routing), and Auth Bypass.
  - **Tier 7 (High):** XXE and Business Logic Race Conditions (limit-overruns).
  - **Attack Chain Discovery:** Correlate isolated Medium anomalies (e.g. CORS preauth token leaks + AI model injection) into High/Critical severity chains."""

if target in text:
    text = text.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("[+] Successfully updated AGENTS.md with HexStrike integration!")
else:
    print("[-] Target not found in AGENTS.md")
