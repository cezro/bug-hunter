with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("54286:")
print("idx of 54286:", idx)
if idx != -1:
    print(content[idx:idx+800])
