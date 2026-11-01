import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Find all url properties
routes = set(re.findall(r'url:\s*["\'](/[^"\']+)["\']', content))
print(f"Total url properties found: {len(routes)}")
for r in sorted(routes):
    print("  ", r)
