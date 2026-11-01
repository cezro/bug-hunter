import subprocess
import re

def fetch(chunk):
    url = f"https://super.hostgator.com.br/_next/static/chunks/{chunk}.js"
    cmd = [
        "curl.exe", "-s",
        "-H", "Referer: https://super.hostgator.com.br/agentes/conhecimento",
        "-A", "Mozilla/5.0",
        url
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

chunks = ["711-9e76270136cec0b6", "79-763abf315b72c7c7", "670-ed0727bb465c596a", "594-717cd23cce9a2d8f"]

for c in chunks:
    text = fetch(c)
    print(f"=== Chunk {c} (Length: {len(text)}) ===")
    if "71241" in text:
        print("  Found module 71241 in", c)
        # Extract snippet around 71241
        idx = text.find("71241:")
        print("  Snippet:", text[idx:idx+800])
