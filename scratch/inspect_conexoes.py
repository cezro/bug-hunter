import subprocess
import re

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/pages/agentes/conexoes-b5924e2ec0a6c97a.js"

r = subprocess.run([
    "curl.exe", "-s",
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout
print(f"Length of conexoes chunk: {len(content)}")

# Find all string literals longer than 3 chars
strings = set(re.findall(r'["\']([^"\'\n\r\t]{4,100})["\']', content))
print("Interesting strings in conexoes:")
for s in sorted(strings):
    if any(k in s.lower() for k in ["api", "connect", "channel", "graphql", "whatsapp", "agent", "token", "http"]):
        print("  ", s)
