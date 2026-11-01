import subprocess
import re

cmd = ["curl.exe", "-s", "-L", "-A", "Mozilla/5.0", "https://www.hostgator.com.br/supergator"]
res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
html = res.stdout

links = re.findall(r'href=["\']([^"\']+)["\']', html)
print(f"Total links on /supergator: {len(links)}")
for l in sorted(set(links)):
    if any(k in l for k in ["app", "painel", "login", "portal", "supergator", "agent", "dashboard", "checkout", "carrinho", "financeiro"]):
        print("  ", l)
