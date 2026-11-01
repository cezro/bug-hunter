import subprocess

endpoints = [
    "/includes/api.php",
    "/api.php",
    "/oauth/token.php",
    "/oauth/v1",
    "/viewinvoice.php",
    "/clientarea.php",
    "/pwreset.php",
    "/register.php",
    "/cart.php",
    "/submitticket.php",
    "/announcements.php",
    "/knowledgebase.php",
    "/serverstatus.php",
    "/contact.php",
    "/download.php",
    "/index.php?rp=/login",
    "/index.php?rp=/password/reset",
    "/api/v1",
    "/api/v2",
    "/api/chat",
    "/api/ai",
    "/api/vps",
]

base = "https://financeiro.hostgator.com.br"

for ep in endpoints:
    url = base + ep
    cmd = ["curl.exe", "-s", "-o", "NUL", "-w", "%{http_code} %{url_effective}", "-L", "-A", "Mozilla/5.0", url]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"{ep:<25} -> {res.stdout.strip()}")
