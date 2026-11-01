import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("28553:")
sub = content[idx:idx+55000]

# Look for where 28553 ends or where tp is assigned
matches = [m.start() for m in re.finditer(r'tp\s*=', sub)]
print("tp= matches:", matches)
for m in matches:
    print(sub[max(0, m-100):min(len(sub), m+300)])
    print("-" * 40)
