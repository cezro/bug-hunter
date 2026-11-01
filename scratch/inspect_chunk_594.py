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
print(f"Length of chunk 594: {len(content)}")

# Find all string literals
strings = set(re.findall(r'["\']([^"\'\n\r\t]{4,100})["\']', content))
print("Interesting strings in chunk 594:")
for s in sorted(strings):
    if any(k in s.lower() for k in ["api", "connect", "channel", "graphql", "whatsapp", "agent", "token", "http", "credential", "qr"]):
        print("  ", s)
