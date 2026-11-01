import urllib.request
import re

url = 'https://raw.githubusercontent.com/0x4m4/hexstrike-ai/master/hexstrike_server.py'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

def inspect_class(class_name):
    print(f"\n==========================================")
    print(f"[*] Inspecting Class: {class_name}")
    print(f"==========================================")
    pattern = rf'class\s+{class_name}[:\(].*?(?=\nclass\s+|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        body = match.group(0)
        methods = re.findall(r'def\s+([a-zA-Z0-9_]+)', body)
        print("Methods:", methods)
        print("Preview:\n", body[:1200])
    else:
        print("Class not found directly via regex.")

for c in ['IntelligentDecisionEngine', 'BugBountyWorkflowManager', 'HTTPTestingFramework', 'RateLimitDetector', 'VulnerabilityCorrelator']:
    inspect_class(c)
