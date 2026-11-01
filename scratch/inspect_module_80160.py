import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")
chunk_url = "https://super.hostgator.com.br/_next/static/chunks/pages/_app-55de464cbb88e84e.js"

r = subprocess.run([
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout

idx = content.find("80160:")
if idx != -1:
    print("=== Found module 80160 ===")
    print(content[idx:idx+3500])
else:
    print("Module 80160 not found")
