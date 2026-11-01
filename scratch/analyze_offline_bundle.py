import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print(f"Total bundle length: {len(content)} characters")

# Find module 82477
m = re.search(r'(?:["\']?82477["\']?\s*:\s*\(.*?\)\s*=>\s*\{)', content)
if m:
    start = m.start()
    print(f"\n=== Found module 82477 at {start} ===")
    print(content[start:start+4000])
else:
    print("Module 82477 definition not directly matched with regex, searching broader...")
    for m in re.finditer(r'82477', content):
        idx = m.start()
        print(f"Occurrence at {idx}:", content[max(0, idx-30):min(len(content), idx+100)])

# Search for any axios / fetch / baseUrl configurations
print("\n=== BASE URL / API HOSTS in bundle ===")
matches = set(re.findall(r'(?:baseURL|apiUrl|apiHost|NEXT_PUBLIC_[A-Z0-9_]*|https?://[a-zA-Z0-9\.\-_/]+)', content))
for m in sorted(matches):
    if any(k in m.lower() for k in ["api", "super", "hostgator", "agent", "gateway", "backend", "builderservices", "newfold", "token", "auth", "openai", "claude", "aws", "appsync"]):
        print("  ", m)
