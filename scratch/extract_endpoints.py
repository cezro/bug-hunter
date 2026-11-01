import subprocess
import re
import json

def fetch_with_curl(url):
    cmd = ["curl.exe", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", url]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    return res.stdout

urls = [
    "https://www.hostgator.com.br/_next/static/chunks/pages/all-pass-96fd4c1b4dca967d.js",
    "https://www.hostgator.com.br/_next/static/BP4kncD355Nm_EpCmYmx0/_buildManifest.js",
]

for url in urls:
    print(f"=== Fetching {url} ===")
    content = fetch_with_curl(url)
    print(f"Downloaded {len(content)} bytes")
    
    # If buildManifest, extract all page routes
    if "_buildManifest" in url:
        routes = re.findall(r'["\'](/[^"\']*)["\']:\s*\[', content)
        print("Page Routes in buildManifest:")
        for r in sorted(routes):
            if any(k in r for k in ["ai", "pass", "vps", "agent", "super", "admin", "chat", "bot", "login", "auth"]):
                print("  [HIGH VALUE]", r)
            else:
                print("  ", r)
    else:
        # Extract endpoints
        endpoints = set(re.findall(r'["\'](/(?:api|v[1-9]|auth|ai|admin|vps|checkout)[^"\'\s>]+)["\']', content))
        print("Endpoints found:", len(endpoints))
        for ep in sorted(endpoints):
            print("  ", ep)
            
        # Extract URLs
        full_urls = set(re.findall(r'https?://[a-zA-Z0-9\.\-]+(?:/[^"\'\s<>]*)?', content))
        print("Full URLs found:", len(full_urls))
        for u in sorted(full_urls):
            print("  ", u)
