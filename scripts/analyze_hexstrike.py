import urllib.request
import re

url = 'https://raw.githubusercontent.com/0x4m4/hexstrike-ai/master/hexstrike_server.py'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

print(f"HexStrike Server Size: {len(content):,} bytes")

classes = re.findall(r'class\s+([a-zA-Z0-9_]+)', content)
print("Classes:", classes)

routes = re.findall(r'@app\.(?:route|get|post)\([\'"]([^\'"]+)', content)
print(f"Total Routes: {len(routes)}")
print("Sample Routes:")
for r in routes[:20]:
    print("  ", r)

# Search for agent / intelligence / workflow logic
agents = re.findall(r'(?:agent|pipeline|workflow|chain|decision)', content, re.IGNORECASE)
print(f"Occurrences of workflow/agent keywords: {len(agents)}")
