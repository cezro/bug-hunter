#!/usr/bin/env python3
"""
HexStrike AI Tactical Decision & Vulnerability Prioritization Engine
Inspired by HexStrike AI (0x4m4/hexstrike-ai):
  - 10-Tier Vulnerability Priority Matrix
  - Intelligent Technology-to-Attack Surface Mapping
  - Multi-Stage Attack Chain Discovery
  - Adaptive Timing & WAF Evasion Profiles
"""

import sys
import json
import argparse
import re
from typing import Dict, List, Any

# 10-Tier Bug Bounty Vulnerability Priority Matrix (HexStrike Standard)
VULN_PRIORITY_MATRIX = {
    "RCE": {
        "priority": 10,
        "impact": "Critical",
        "description": "Remote Code Execution / Server-Side Code Injection",
        "test_vectors": ["Template Injection (SSTI)", "Command Injection", "Deserialization", "File Upload to Executable Path"],
        "tools": ["nuclei", "tplmap", "custom-script"]
    },
    "SQLI": {
        "priority": 9,
        "impact": "Critical",
        "description": "SQL Injection & Database Takeover",
        "test_vectors": ["Boolean-based Blind", "Time-based Blind", "Error-based", "Stacked Queries"],
        "tools": ["sqlmap", "ghauri", "nuclei"]
    },
    "IDOR_BOLA": {
        "priority": 8,
        "impact": "High",
        "description": "Insecure Direct Object Reference / Broken Object Level Authorization",
        "test_vectors": ["Integer ID decrement/increment", "UUID swap between tenants", "Role parameter tampering in JSON body", "Array wrapping"],
        "tools": ["arjun", "burp-intruder", "curl"]
    },
    "SSRF": {
        "priority": 8,
        "impact": "High",
        "description": "Server-Side Request Forgery",
        "test_vectors": ["Cloud Metadata (169.254.169.254)", "Internal Gateway APIs", "Webhook URLs", "PDF/Image renderers"],
        "tools": ["interactsh", "nuclei", "ffuf"]
    },
    "AI_GATEWAY_ABUSE": {
        "priority": 8,
        "impact": "High",
        "description": "Arbitrary Model Selection / Enterprise Quota Consumption / LLM Jailbreak",
        "test_vectors": ["Model deployment swapping (gpt-4o/o1)", "System prompt override", "Internal tool call manipulation"],
        "tools": ["custom-json-tester", "curl"]
    },
    "AUTH_BYPASS": {
        "priority": 8,
        "impact": "High",
        "description": "Authentication / 2FA / Session Bypass",
        "test_vectors": ["OAuth redirect_uri manipulation", "JWT alg:none / key confusion", "Response manipulation (false->true)", "Pre-auth token leaks"],
        "tools": ["jwt-tool", "burp-repeater"]
    },
    "XXE": {
        "priority": 7,
        "impact": "High",
        "description": "XML External Entity Injection",
        "test_vectors": ["SAML assertions", "Office doc/SVG parsers", "SOAP APIs"],
        "tools": ["nuclei", "custom-payloads"]
    },
    "RACE_CONDITION": {
        "priority": 7,
        "impact": "High",
        "description": "State Synchronization & Business Logic Race Conditions",
        "test_vectors": ["Limit-overrun (coupons, wallet balances, checkout)", "TOCTOU multi-thread requests", "HTTP/2 single-packet flood"],
        "tools": ["turbo-intruder", "parallel-curl"]
    },
    "CORS_MISCONFIG": {
        "priority": 6,
        "impact": "Medium-High",
        "description": "Credentialed Cross-Origin Resource Sharing on User Subdomains",
        "test_vectors": ["Null origin reflection", "Wildcard user subdomain reflection with credentials:true", "Internal intranet origins"],
        "tools": ["corsy", "curl"]
    },
    "XSS_STORED": {
        "priority": 6,
        "impact": "Medium",
        "description": "Stored Cross-Site Scripting (Privileged Context)",
        "test_vectors": ["Admin panel profile/bio fields", "Store product descriptions", "File upload metadata"],
        "tools": ["dalfox", "nuclei"]
    }
}

# Technology-Specific Attack Patterns
TECH_STACK_RULES = {
    "wordpress": {
        "high_priority_checks": ["IDOR in REST API (/wp-json/)", "Plugin CVEs via Nuclei", "Open user registration routes", "XML-RPC brute force"],
        "recommended_tools": ["wpscan", "nuclei", "wp-json-auditor"]
    },
    "azure_openai": {
        "high_priority_checks": ["Arbitrary Model Parameter Tampering", "Enterprise Quota Exhaustion", "Prompt Injection in Tool Calls", "Citations Blob Leakage"],
        "recommended_tools": ["custom-ai-tester", "curl"]
    },
    "cloudflare": {
        "waf_evasion_strategy": "Rotate User-Agent, throttle to <=3 req/s, mimic browser TLS fingerprints, avoid aggressive scanner headers",
        "timing_profile": "conservative"
    },
    "react_microfrontends": {
        "high_priority_checks": ["Exposed webpack source maps", "Client-side API keys in bundles", "Unlinked admin routes in SystemJS manifests"],
        "recommended_tools": ["audit_bundles.py", "sourcemapper"]
    }
}

# Adaptive Timing Profiles
TIMING_PROFILES = {
    "aggressive": {"delay_sec": 0.1, "max_concurrency": 20, "timeout_sec": 5, "use_when": "No WAF, internal test instance"},
    "normal": {"delay_sec": 0.5, "max_concurrency": 10, "timeout_sec": 10, "use_when": "Standard cloud target with mild throttling"},
    "conservative": {"delay_sec": 1.5, "max_concurrency": 3, "timeout_sec": 15, "use_when": "Cloudflare / Akamai present, avoid IP bans"},
    "stealth": {"delay_sec": 3.0, "max_concurrency": 1, "timeout_sec": 25, "use_when": "Aggressive WAF, high-risk detection target"}
}

def analyze_target_attack_surface(domain: str, tech_stack: List[str], observed_endpoints: List[str] = None) -> Dict[str, Any]:
    """Generates an intelligent HexStrike decision plan for a target."""
    tech_lower = [t.lower() for t in tech_stack]
    
    # 1. Determine optimal timing profile
    timing_profile = "normal"
    if any(w in tech_lower for w in ["cloudflare", "akamai", "imperva", "fastly"]):
        timing_profile = "conservative"
        
    # 2. Select prioritized vulnerability classes
    recommended_attacks = []
    for vuln_key, details in VULN_PRIORITY_MATRIX.items():
        relevance_score = details["priority"]
        reasons = []
        
        # Correlate with tech stack
        if "wordpress" in tech_lower and vuln_key in ["IDOR_BOLA", "AUTH_BYPASS"]:
            relevance_score += 2
            reasons.append("WordPress detected: audit /wp-json/ endpoints for missing authorization")
        if "azure_openai" in tech_lower and vuln_key in ["AI_GATEWAY_ABUSE", "SSRF"]:
            relevance_score += 3
            reasons.append("AI Gateway detected: test for model tampering and enterprise quota exhaustion")
        if any(e for e in (observed_endpoints or []) if "preauth" in e or "session" in e) and vuln_key == "CORS_MISCONFIG":
            relevance_score += 2
            reasons.append("Session/preauth endpoints observed: test credentialed CORS reflection")
            
        recommended_attacks.append({
            "vuln_class": vuln_key,
            "priority_score": relevance_score,
            "impact": details["impact"],
            "description": details["description"],
            "test_vectors": details["test_vectors"],
            "reasons": reasons
        })
        
    recommended_attacks.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # 3. Discover multi-stage attack chains
    attack_chains = []
    if any("preauth" in (e or "") for e in (observed_endpoints or [])) and "azure_openai" in tech_lower:
        attack_chains.append({
            "chain_name": "CORS Token Extraction -> Enterprise AI Gateway Resource Exhaustion",
            "stages": [
                "Stage 1: Exploit CORS misconfiguration on user subdomain to read X-CSRF-TOKEN and user Bearer JWT",
                "Stage 2: Leverage stolen Bearer JWT to invoke /ai-api/v3.0/chat",
                "Stage 3: Tamper with OpenAiChatOptions.Model to force enterprise GPT-4o execution, consuming enterprise budget"
            ],
            "estimated_impact": "High (P1/P2)"
        })
        
    return {
        "target": domain,
        "tech_stack": tech_stack,
        "timing_profile": {
            "name": timing_profile,
            "specs": TIMING_PROFILES[timing_profile]
        },
        "prioritized_attack_classes": recommended_attacks[:5],
        "attack_chains": attack_chains
    }

def main():
    parser = argparse.ArgumentParser(description="HexStrike AI Tactical Decision Engine")
    parser.add_argument("domain", help="Target domain (e.g. bluehost.com, app.web.com)")
    parser.add_argument("--tech", nargs="*", default=["Cloudflare", "WordPress", "Azure_OpenAI"], help="Detected tech stack")
    parser.add_argument("--endpoints", nargs="*", default=["/sfcore.do?getJWTTokenV1", "/accounts/v1.0/session/preauth", "/ai-api/v3.0/chat"], help="Observed endpoints")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()
    
    plan = analyze_target_attack_surface(args.domain, args.tech, args.endpoints)
    
    if args.json:
        print(json.dumps(plan, indent=2))
        return
        
    print("=" * 65)
    print(f"[*] HEXSTRIKE AI TACTICAL ASSESSMENT: {args.domain.upper()}")
    print("=" * 65)
    print(f"[+] Detected Tech Stack: {', '.join(args.tech)}")
    print(f"[+] Selected Timing Profile: {plan['timing_profile']['name'].upper()} ({plan['timing_profile']['specs']['delay_sec']}s delay, {plan['timing_profile']['specs']['max_concurrency']} concurrency)")
    print(f"    Reason: {plan['timing_profile']['specs']['use_when']}")
    
    print("\n[+] TOP 5 PRIORITIZED ATTACK CLASSES:")
    for i, atk in enumerate(plan["prioritized_attack_classes"], 1):
        print(f"  {i}. [{atk['impact'].upper()}] {atk['vuln_class']} (Score: {atk['priority_score']})")
        print(f"     Description: {atk['description']}")
        print(f"     Key Vectors: {', '.join(atk['test_vectors'][:2])}")
        if atk["reasons"]:
            print(f"     Context Hint: {atk['reasons'][0]}")
            
    if plan["attack_chains"]:
        print("\n[!] MULTI-STAGE ATTACK CHAINS DISCOVERED:")
        for chain in plan["attack_chains"]:
            print(f"  --> Chain: {chain['chain_name']} ({chain['estimated_impact']})")
            for stage in chain["stages"]:
                print(f"      - {stage}")
    print("=" * 65)

if __name__ == "__main__":
    main()
