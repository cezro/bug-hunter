with open("scratch/app_bundle.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = 81902
# search for let d= or var d=
sub = content[idx:idx+3000]
for line in sub.split(";"):
    if "d=" in line or "p=" in line or "l=" in line:
        print(line)
