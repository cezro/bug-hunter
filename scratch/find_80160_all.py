import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

chunks = [
    "static/chunks/899-f7ae10480fdc75f6.js",
    "static/chunks/main-d273e3732dd3c28f.js",
    "static/chunks/711-9e76270136cec0b6.js",
    "static/chunks/750-cdbecd8ba34ae34f.js",
    "static/chunks/129-0d16f600b4e911fc.js",
    "static/chunks/179-d007fae848717edd.js",
    "static/chunks/594-717cd23cce9a2d8f.js",
]

for c in chunks:
    chunk_url = f"https://super.hostgator.com.br/_next/{c}"
    r = subprocess.run([
        "curl.exe", "-s", "-b", cookie_file,
        "-H", "Referer: https://super.hostgator.com.br/login",
        "-H", "User-Agent: Mozilla/5.0",
        chunk_url
    ], stdout=subprocess.PIPE, text=True, errors="ignore")
    content = r.stdout
    if "80160:" in content:
        print(f"=== Found 80160 in {c} ===")
        idx = content.find("80160:")
        print(content[idx:idx+3500])
        break
