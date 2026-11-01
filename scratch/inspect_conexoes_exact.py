import subprocess
import re

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/pages/agentes/conexoes-b5924e2ec0a6c97a.js"

r = subprocess.run([
    "curl.exe", "-s",
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-A", "Mozilla/5.0",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout

idx = content.find("getAgentCredentials")
if idx != -1:
    print(content[max(0, idx - 200):min(len(content), idx + 300)])
