with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("82477:")
if idx != -1:
    print(content[idx+3500:idx+10000])
