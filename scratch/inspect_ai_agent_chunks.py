import subprocess
import re
import json

chunks = [
    "static/chunks/pages/agentes-69b3d42dce334158.js",
    "static/chunks/pages/agentes/criar-791c57ff8e6d0d2c.js",
    "static/chunks/pages/agentes/configurar-0a7fb292a84ca2f1.js",
    "static/chunks/pages/agentes/conhecimento-2cb68272b67f0e1c.js",
    "static/chunks/pages/agentes/conexoes-b5924e2ec0a6c97a.js",
    "static/chunks/pages/agentes/conversas-6f3acc0be9e3a55b.js",
    "static/chunks/pages/cadastro-90bf325018d2f5be.js",
    "static/chunks/pages/cadastro/dados-e20ad11806765011.js",
    "static/chunks/pages/checkout-b468c1a0842b3304.js",
    "static/chunks/pages/onboarding-a494f2b03f1592e5.js",
]

def fetch_chunk(path):
    url = f"https://super.hostgator.com.br/_next/{path}"
    cmd = [
        "curl.exe", "-s",
        "-H", "Referer: https://super.hostgator.com.br/login",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        url
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

all_api_endpoints = set()
all_urls = set()

for c in chunks:
    text = fetch_chunk(c)
    print(f"=== {c} (Length: {len(text)}) ===")
    
    # Extract API endpoints
    apis = re.findall(r'["\'](/(?:api|v[1-9]|auth|agentes?|bot|chat|ai|knowledge|leads?|users?|webhooks?|sso)[^"\'\s>]+)["\']', text)
    for a in apis:
        all_api_endpoints.add(a)
        
    # Extract URLs
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-]+(?:/[a-zA-Z0-9_\-\./\?=%&]*)?', text)
    for u in urls:
        if not any(ign in u for ign in ["w3.org", "google", "cloudflare", "facebook", "twitter", "schema.org"]):
            all_urls.add(u)

print("\n=== DISCOVERED API ENDPOINTS ===")
for ep in sorted(all_api_endpoints):
    print("  ", ep)

print("\n=== DISCOVERED EXTERNAL / BACKEND URLS ===")
for u in sorted(all_urls):
    print("  ", u)
