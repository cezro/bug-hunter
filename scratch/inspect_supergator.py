import subprocess
import re

def fetch(url):
    cmd = ["curl.exe", "-s", "-L", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", url]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

targets = [
    "https://www.hostgator.com.br/supergator",
    "https://www.hostgator.com.br/servidor-vps/gatorclaw",
    "https://www.hostgator.com.br/servidor-vps/openclaw",
    "https://www.hostgator.com.br/servidor-vps/hospedagem-n8n",
    "https://www.hostgator.com.br/all-pass-sem-limite",
]

for t in targets:
    html = fetch(t)
    print(f"=== {t} (Length: {len(html)}) ===")
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.I)
    if title:
        print("  Title:", title.group(1))
    # Look for API calls, endpoints, iframes, action urls
    apis = set(re.findall(r'https?://[a-zA-Z0-9\.\-]+(?:/[a-zA-Z0-9_\-\./\?=%&]*)?', html))
    print("  Interesting URLs/APIs:")
    for a in sorted(apis):
        if any(k in a.lower() for k in ["api", "supergator", "openclaw", "gatorclaw", "n8n", "auth", "token", "ai", "financeiro"]):
            print("    ", a)
