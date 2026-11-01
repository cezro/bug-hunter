with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("mountTrainAgentFormData")
print("idx:", idx)
if idx != -1:
    print(content[idx:idx+1200])
