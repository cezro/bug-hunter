with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("GET_LEADS_SUCCESS")
if idx != -1:
    print(content[max(0, idx - 800):min(len(content), idx + 800)])
