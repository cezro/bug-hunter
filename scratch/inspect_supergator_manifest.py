import subprocess
import re
import json

def fetch_chunk(url, referer="https://super.hostgator.com.br/login"):
    cmd = [
        "curl.exe", "-s",
        "-H", f"Referer: {referer}",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        url
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

# 1. Fetch _buildManifest.js
manifest_text = fetch_chunk("https://super.hostgator.com.br/_next/static/pV5ArJxHupOao-0NHHlli/_buildManifest.js")
print("Manifest length:", len(manifest_text))

routes = re.findall(r'["\'](/[^"\']*)["\']:\s*\[([^\]]*)\]', manifest_text)
print(f"Total routes found in SuperGator manifest: {len(routes)}")
for r, chunks in routes:
    print(f"Route: {r}")
    chunk_files = re.findall(r'["\']([^"\']+\.js)["\']', chunks)
    for cf in chunk_files:
        print(f"   chunk: {cf}")

# Let's inspect chunk 42626 or other core chunks (b._.urls)
# Let's search manifest_text for chunks
all_chunks = set(re.findall(r'static/chunks/[^"\']+\.js', manifest_text))
print(f"\nAll unique chunks ({len(all_chunks)}):")
for c in sorted(all_chunks):
    print(" ", c)
