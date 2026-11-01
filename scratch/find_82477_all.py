import subprocess
import os

cookie_file = os.path.abspath("scratch/cf_cookies.txt")

subprocess.run([
    "curl.exe", "-s", "-c", cookie_file,
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "https://super.hostgator.com.br/login"
], stdout=subprocess.DEVNULL)

chunks = [
    "static/chunks/899-f7ae10480fdc75f6.js",
    "static/chunks/main-d273e3732dd3c28f.js",
    "static/chunks/711-9e76270136cec0b6.js",
    "static/chunks/750-cdbecd8ba34ae34f.js",
    "static/chunks/129-0d16f600b4e911fc.js",
    "static/chunks/179-d007fae848717edd.js",
    "static/chunks/285-765d2dc22420bd8f.js",
    "static/chunks/366-9ed234be95b339df.js",
    "static/chunks/384-b92de78cbeedcfbb.js",
    "static/chunks/594-717cd23cce9a2d8f.js",
    "static/chunks/670-ed0727bb465c596a.js",
    "static/chunks/79-763abf315b72c7c7.js",
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
    if "82477:" in content:
        print(f"=== Found 82477 in {c} ===")
        idx = content.find("82477:")
        print(content[idx:idx+4500])
        break
