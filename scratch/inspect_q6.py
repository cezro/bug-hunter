with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("Q6:")
print("idx of Q6:", idx)
while idx != -1:
    print(content[max(0, idx - 50):min(len(content), idx + 250)])
    print("=" * 50)
    idx = content.find("Q6:", idx + 1)
