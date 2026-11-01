with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("aiPlatformCore")
print("idx of aiPlatformCore:", idx)
while idx != -1:
    print(content[max(0, idx - 100):min(len(content), idx + 300)])
    print("=" * 50)
    idx = content.find("aiPlatformCore", idx + 1)
