import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("=== Redux slice around getAgentCredentials (x.fulfilled) ===")
for m in re.finditer(r"agent/getAgentCredentials", text):
    start = max(0, m.start() - 200)
    end = min(len(text), m.end() + 2500)
    print(text[start:end])
    print("=" * 60)

print("=== Auth Service Module & SSO Back (87140) ===")
for m in re.finditer(r"87140:\(e,t,r\)=>", text):
    start = m.start()
    end = min(len(text), m.start() + 4000)
    print(text[start:end])
    print("=" * 60)
