with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("28553:")
sub = content[idx:idx+55000]
idx_tp = sub.find("let tp=")
print(sub[max(0, idx_tp - 1500):idx_tp + 200])
