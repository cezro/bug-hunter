import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

# First, hit /login to get valid cf_bm cookie
cmd_login = [
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "https://super.hostgator.com.br/login"
]
subprocess.run(cmd_login, stdout=subprocess.DEVNULL)

with open(cookie_file, "r") as f:
    print("Cookies saved:\n", f.read())

# Now fetch chunk 711
cmd_chunk = [
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "https://super.hostgator.com.br/_next/static/chunks/711-9e76270136cec0b6.js"
]
res = subprocess.run(cmd_chunk, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
print(f"Chunk 711 response length: {len(res.stdout)}")
print("First 300 chars:\n", res.stdout[:300])
