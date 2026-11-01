import subprocess
import re

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/594-717cd23cce9a2d8f.js"

r = subprocess.run([
    "curl.exe", "-s",
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout

idx = content.find("getAgentCredentials")
while idx != -1:
    print(f"=== getAgentCredentials at {idx} ===")
    print(content[max(0, idx - 200):min(len(content), idx + 500)])
    print("-" * 50)
    idx = content.find("getAgentCredentials", idx + 1)
