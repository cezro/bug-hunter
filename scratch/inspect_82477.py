import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

subprocess.run([
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "https://super.hostgator.com.br/login"
], stdout=subprocess.DEVNULL)

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/pages/_app-55de464cbb88e84e.js"

r = subprocess.run([
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout

idx = content.find("82477:")
print("idx of 82477:", idx)
if idx != -1:
    print(content[idx:idx+4500])
