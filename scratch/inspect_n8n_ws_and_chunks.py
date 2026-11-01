import re

with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("=== Rest of extraReducers in M (around D.rejected) ===")
for m in re.finditer(r"e\.addCase\(D\.rejected", text):
    print(text[m.start():m.start()+2500])
    print("=" * 60)

print("=== Search for n8nWebsocket / wss-chat / ngrok ===")
for kw in ["n8nWebsocket", "wss-chat", "ngrok", "getAgentCredentials", "growthbook"]:
    print(f"--- Keyword: {kw} ---")
    for m in re.finditer(re.escape(kw), text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 400)
        print(text[start:end])
        print("-" * 40)
