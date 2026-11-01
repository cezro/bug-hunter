import subprocess
import re

def fetch_chunk(path):
    url = f"https://super.hostgator.com.br/_next/{path}"
    cmd = [
        "curl.exe", "-s",
        "-H", "Referer: https://super.hostgator.com.br/login",
        "-A", "Mozilla/5.0",
        url
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

chunks = [
    "static/chunks/pages/_app-55de464cbb88e84e.js",
    "static/chunks/750-cdbecd8ba34ae34f.js",
    "static/chunks/366-9ed234be95b339df.js",
    "static/chunks/384-b92de78cbeedcfbb.js",
    "static/chunks/594-717cd23cce9a2d8f.js",
    "static/chunks/670-ed0727bb465c596a.js",
    "static/chunks/711-9e76270136cec0b6.js",
    "static/chunks/899-f7ae10480fdc75f6.js",
]

for c in chunks:
    text = fetch_chunk(c)
    print(f"=== {c} (Length: {len(text)}) ===")
    
    # Search for baseUrl, NEXT_PUBLIC, api, backend, hostgator
    matches = re.findall(r'(?:baseURL|apiUrl|apiHost|NEXT_PUBLIC[A-Z0-9_]*|https?://[a-zA-Z0-9\.\-_/]+)', text)
    filtered = set()
    for m in matches:
        if any(k in m.lower() for k in ["api", "super", "hostgator", "agent", "backend", "builderservices", "newfold", "token", "auth"]):
            filtered.add(m)
    for f in sorted(filtered)[:20]:
        print("  ", f)
