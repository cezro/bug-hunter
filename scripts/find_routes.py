import urllib.request
import re

url = "https://app.web.com/3543/main.bundle.js"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        text = resp.read().decode('utf-8', errors='ignore')
        matches = set(re.findall(r'["\'](/[a-zA-Z0-9_/-]*(?:signup|register|trial|onboarding|free|flow)[a-zA-Z0-9_/-]*)["\']', text))
        print(f"Found {len(matches)} matching paths:")
        for m in sorted(matches):
            print("  ", m)
except Exception as e:
    print("Error:", e)
