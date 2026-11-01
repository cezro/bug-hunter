import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

headers = [
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "-H", "Accept: */*",
    "-H", "Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "-H", "Referer: https://super.hostgator.com.br/login",
    "-H", "Sec-Ch-Ua: \"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
    "-H", "Sec-Ch-Ua-Mobile: ?0",
    "-H", "Sec-Ch-Ua-Platform: \"Windows\"",
    "-H", "Sec-Fetch-Dest: script",
    "-H", "Sec-Fetch-Mode: no-cors",
    "-H", "Sec-Fetch-Site: same-origin",
]

cmd = ["curl.exe", "-s", "-b", cookie_file] + headers + [
    "-o", "scratch/app_bundle.js",
    "https://super.hostgator.com.br/_next/static/chunks/pages/_app-55de464cbb88e84e.js"
]

subprocess.run(cmd)
size = os.path.getsize("scratch/app_bundle.js")
print(f"Downloaded: {size} bytes")
