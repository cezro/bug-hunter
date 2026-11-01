with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("28553:")
print("idx of 28553:", idx)
if idx != -1:
    print(content[idx:idx+2500])
