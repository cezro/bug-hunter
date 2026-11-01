import subprocess
import os
import re

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

# Ensure cookie is fresh
cmd_login = [
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "https://super.hostgator.com.br/login"
]
subprocess.run(cmd_login, stdout=subprocess.DEVNULL)

chunks = [
    "static/chunks/129-0d16f600b4e911fc.js",
    "static/chunks/179-d007fae848717edd.js",
    "static/chunks/285-765d2dc22420bd8f.js",
    "static/chunks/366-9ed234be95b339df.js",
    "static/chunks/384-b92de78cbeedcfbb.js",
    "static/chunks/594-717cd23cce9a2d8f.js",
    "static/chunks/670-ed0727bb465c596a.js",
    "static/chunks/711-9e76270136cec0b6.js",
    "static/chunks/750-cdbecd8ba34ae34f.js",
    "static/chunks/79-763abf315b72c7c7.js",
    "static/chunks/899-f7ae10480fdc75f6.js",
    "static/chunks/pages/agentes-69b3d42dce334158.js",
    "static/chunks/pages/agentes/calendario-333fd775cd2da878.js",
    "static/chunks/pages/agentes/calendario/conectar-4881c5180057ee03.js",
    "static/chunks/pages/agentes/calendario/configuracoes-29796c7ed9aca463.js",
    "static/chunks/pages/agentes/clientes-6995ce36d0916a8f.js",
    "static/chunks/pages/agentes/conexoes-b5924e2ec0a6c97a.js",
    "static/chunks/pages/agentes/configurar-0a7fb292a84ca2f1.js",
    "static/chunks/pages/agentes/conhecimento-2cb68272b67f0e1c.js",
    "static/chunks/pages/agentes/conversas-6f3acc0be9e3a55b.js",
    "static/chunks/pages/agentes/criar-791c57ff8e6d0d2c.js",
    "static/chunks/pages/assinatura-0b89524706171a5d.js",
    "static/chunks/pages/cadastro-90bf325018d2f5be.js",
    "static/chunks/pages/cadastro/dados-e20ad11806765011.js",
    "static/chunks/pages/checkout-b468c1a0842b3304.js",
    "static/chunks/pages/index-17425dfb1b130895.js",
    "static/chunks/pages/login-5335884822c40733.js",
    "static/chunks/pages/onboarding-a494f2b03f1592e5.js",
    "static/chunks/pages/perfil-c1ac19c0ad036349.js",
    "static/chunks/pages/selecionar-plano-42e559df25bd6fdd.js",
]

print(f"Scanning {len(chunks)} chunks...")
all_endpoints = set()
all_urls = set()

for c in chunks:
    chunk_url = f"https://super.hostgator.com.br/_next/{c}"
    r = subprocess.run([
        "curl.exe", "-s", "-b", cookie_file,
        "-H", "Referer: https://super.hostgator.com.br/login",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        chunk_url
    ], stdout=subprocess.PIPE, text=True, errors="ignore")
    content = r.stdout
    
    if len(content) < 1000 or "<!DOCTYPE html>" in content[:100]:
        continue
        
    # Check for endpoints
    eps = re.findall(r'["\'](/(?:api|v[1-9]|auth|agente[s]?|bot|chat|ai|knowledge|leads?|users?|webhooks?|sso|graphql)[^"\'\s>]+)["\']', content)
    for ep in eps:
        all_endpoints.add(ep)
        
    # Check for URLs
    urls = re.findall(r'https?://[a-zA-Z0-9\.\-]+(?:/[a-zA-Z0-9_\-\./\?=%&]*)?', content)
    for u in urls:
        if not any(ign in u for ign in ["w3.org", "google", "cloudflare", "facebook", "twitter", "schema.org", "googletagmanager", "recaptcha"]):
            all_urls.add(u)
            
    # Check for target logic
    if any(k in content for k in ["getAgentById", "createAgent", "updateAgent", "deleteAgent", "trainAgent"]):
        print(f"[!] Target logic found in chunk: {c} (Length: {len(content)})")
        for m in re.finditer(r'(?:getAgentById|createAgent|updateAgent|deleteAgent|trainAgent|baseURL|apiUrl)[^;]{10,200}', content):
            snippet = m.group(0)
            print("    Snippet:", snippet)

print("\n==========================================")
print(f"[*] ALL UNIQUE API ENDPOINTS ({len(all_endpoints)}):")
for ep in sorted(all_endpoints):
    print("  ", ep)

print("\n==========================================")
print(f"[*] ALL UNIQUE BACKEND / TARGET URLS ({len(all_urls)}):")
for u in sorted(all_urls):
    print("  ", u)
