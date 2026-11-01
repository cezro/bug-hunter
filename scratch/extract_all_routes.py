import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Find all API routes called via tp / tc / axios
routes = set(re.findall(r'(?:get|post|put|patch|delete)\(["\'](/[^"\']+)["\']', content))
print(f"Total API routes found: {len(routes)}")
for r in sorted(routes):
    print("  ", r)
