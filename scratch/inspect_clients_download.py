with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("/api/clients/download")
print("idx of /api/clients/download:", idx)
if idx != -1:
    print(content[max(0, idx - 200):min(len(content), idx + 500)])
