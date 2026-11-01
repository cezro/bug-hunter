import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

chunks = [
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

for c in chunks:
    chunk_url = f"https://super.hostgator.com.br/_next/{c}"
    r = subprocess.run([
        "curl.exe", "-s", "-b", cookie_file,
        "-H", "Referer: https://super.hostgator.com.br/login",
        "-H", "User-Agent: Mozilla/5.0",
        chunk_url
    ], stdout=subprocess.PIPE, text=True, errors="ignore")
    content = r.stdout
    
    if "graphql" in content.lower():
        print(f"=== FOUND GRAPHQL IN {c} ===")
        idx = content.lower().find("graphql")
        start = max(0, idx - 200)
        end = min(len(content), idx + 400)
        print(content[start:end])
        print("-------------------------------")
