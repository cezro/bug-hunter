with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("AUTH_TOKEN:")
print("idx of AUTH_TOKEN:", idx)
if idx != -1:
    print(content[idx:idx+300])
