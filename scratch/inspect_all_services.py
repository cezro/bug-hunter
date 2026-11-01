import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("=== Occurrences of getAgentCredentials ===")
for m in re.finditer(r"getAgentCredentials", text):
    start = max(0, m.start() - 300)
    end = min(len(text), m.end() + 500)
    print(text[start:end])
    print("-" * 50)

print("=== All API service calls (.u.get / .u.post / .u.patch / .u.put / .u.delete) ===")
for m in re.finditer(r"\.u\.(get|post|patch|put|delete)\(", text):
    start = max(0, m.start() - 250)
    end = min(len(text), m.end() + 250)
    print(text[start:end])
    print("-" * 50)
