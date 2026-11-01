import subprocess
import os
import re

cookie_file = os.path.abspath("scratch/cf_cookies.txt")
chunk_url = "https://super.hostgator.com.br/_next/static/chunks/594-717cd23cce9a2d8f.js"

r = subprocess.run([
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout

idx = content.find("getAgentCredentials")
# search backwards for var x= or let x= or x=s(...)
sub = content[:idx]
imports = re.findall(r'(\b[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+\([0-9]+\))', sub)
print("Recent imports before getAgentCredentials:")
for imp in imports[-15:]:
    print(" ", imp)
