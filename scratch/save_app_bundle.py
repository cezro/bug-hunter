import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

subprocess.run([
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "https://super.hostgator.com.br/login"
], stdout=subprocess.DEVNULL)

chunk_url = "https://super.hostgator.com.br/_next/static/chunks/pages/_app-55de464cbb88e84e.js"

subprocess.run([
    "curl.exe", "-s", "-b", cookie_file,
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "User-Agent: Mozilla/5.0",
    "-o", "scratch/app_bundle.js",
    chunk_url
])

size = os.path.getsize("scratch/app_bundle.js")
print(f"Saved scratch/app_bundle.js: {size} bytes")
