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

idx = content.find("appsync-api")
if idx != -1:
    print("=== SNIPPET AROUND appsync-api ===")
    print(content[max(0, idx - 400):min(len(content), idx + 1200)])

idx2 = content.find("createAgentChannelConnection")
if idx2 != -1:
    print("\n=== SNIPPET AROUND createAgentChannelConnection ===")
    print(content[max(0, idx2 - 400):min(len(content), idx2 + 1200)])
