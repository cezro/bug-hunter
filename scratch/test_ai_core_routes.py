import subprocess

routes = [
    "/omnichannel/agents",
    "/omnichannel/agents/1",
    "/omnichannel/agents/1/training",
    "/omnichannel/agents/1/credentials",
    "/omnichannel/agents/1/test",
    "/business/suggestion",
    "/user/me",
    "/user/credit-card",
    "/credits/checkout",
    "/credits/free-offer/redeem",
    "/invoices",
    "/notifications",
    "/calendar",
    "/product/contracted",
    "/product/trial-subscribe",
    "/login",
    "/register",
    "/refresh-token",
    "/social/login",
    "/auth/sso-back",
]

base = "https://ai-core.hostgator.com.br/api"

for r in routes:
    url = base + r
    cmd = ["curl.exe", "-s", "-o", "NUL", "-w", "%{http_code}", "-H", "Accept: application/json", url]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    code = res.stdout.strip()
    status = "REGISTERED (AUTH REQUIRED)" if code == "401" else ("PUBLIC / REQ_ERROR" if code in ["422", "400", "200"] else code)
    print(f"{r:<35} -> {code} ({status})")
