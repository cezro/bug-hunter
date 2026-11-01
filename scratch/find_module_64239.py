import subprocess
import os

chunks = [
    "static/chunks/129-0d16f600b4e911fc.js",
    "static/chunks/179-d007fae848717edd.js",
    "static/chunks/285-765d2dc22420bd8f.js",
    "static/chunks/366-9ed234be95b339df.js",
    "static/chunks/384-b92de78cbeedcfbb.js",
    "static/chunks/594-717cd23cce9a2d8f.js",
    "static/chunks/670-ed0727bb465c596a.js",
    "static/chunks/711-9e76270136cec0b6.js",
    "static/chunks/750-cdbecd8ba34ae34f.js",
    "static/chunks/79-763abf315b72c7c7.js",
    "static/chunks/899-f7ae10480fdc75f6.js",
    "static/chunks/main-d273e3732dd3c28f.js",
    "static/chunks/pages/_app-55de464cbb88e84e.js",
]

for c in chunks:
    chunk_url = f"https://super.hostgator.com.br/_next/{c}"
    r = subprocess.run([
        "curl.exe", "-s",
        "-H", "Referer: https://super.hostgator.com.br/login",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        chunk_url
    ], stdout=subprocess.PIPE, text=True, errors="ignore")
    content = r.stdout
    if "64239:" in content:
        print(f"=== Found module 64239 in {c} ===")
        idx = content.find("64239:")
        print(content[idx:idx+1500])
