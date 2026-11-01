import subprocess
import os
import re

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

# Login first to refresh cf_bm cookie
subprocess.run([
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "https://super.hostgator.com.br/login"
], stdout=subprocess.DEVNULL)

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/pages/_app-55de464cbb88e84e.js"

r = subprocess.run([
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    chunk_url
], stdout=subprocess.PIPE, text=True, errors="ignore")
content = r.stdout
print("len of _app:", len(content))

matches = [m.start() for m in re.finditer(r'80160', content)]
print(f"Matches for 80160: {len(matches)}")
for idx in matches:
    print(f"Match at {idx}:")
    print(content[max(0, idx - 50):min(len(content), idx + 250)])
    print("-" * 50)
