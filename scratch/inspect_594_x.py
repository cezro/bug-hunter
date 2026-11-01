import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

# Login to refresh cookie
subprocess.run([
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "https://super.hostgator.com.br/login"
], stdout=subprocess.DEVNULL)

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/594-717cd23cce9a2d8f.js"

r = subprocess.run([
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout
print("len:", len(content))

idx = content.find("getAgentCredentials")
print("idx:", idx)
if idx != -1:
    print(content[max(0, idx - 400):min(len(content), idx + 200)])
