import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("=== Redux extraReducers in M ===")
for m in re.finditer(r"extraReducers:e=>\{e\.addCase\(u\.pending", text):
    print(text[m.start():m.start()+5000])
    print("=" * 60)

print("=== Module 42626 (Config & URLs) ===")
for m in re.finditer(r"42626:\(e,t,r\)=>", text):
    print(text[m.start():m.start()+3000])
    print("=" * 60)
