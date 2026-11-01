#!/usr/bin/env python3
"""
Automated 3-Pillar Bug Bounty Recon Pipeline
Inspired by CyberFlow ("I Automated My Entire Bug Bounty Workflow"):
  1. Subdomain Discovery & Diff Monitoring
  2. Smart Port Scanning & Liveness Enumeration
  3. Visual Recon (Headless Screenshots) & Tech Stack Identification
"""

import os
import sys
import json
import urllib.request
import urllib.error
import re
import socket
import subprocess
import argparse
from datetime import datetime

# Browser path for headless screenshots
CHROME_PATH = r"C:\Users\Zero\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

COMMON_PORTS = [80, 443, 8080, 8443, 8000, 9000, 8888, 3000, 5000]

def query_crtsh(domain):
    """Query Certificate Transparency logs via crt.sh JSON API."""
    print(f"[*] Querying crt.sh for domain: {domain}...", flush=True)
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    subdomains = set()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            for entry in data:
                name = entry.get('name_value', '')
                for sub in name.split('\n'):
                    sub = sub.strip().lower()
                    if '*' in sub:
                        sub = sub.replace('*.', '')
                    if sub.endswith(domain) and sub:
                        subdomains.add(sub)
        print(f"[+] crt.sh found {len(subdomains)} unique subdomain(s).")
    except Exception as e:
        print(f"[-] crt.sh query failed: {e}")
    return sorted(list(subdomains))

def diff_monitoring(target_slug, current_subdomains):
    """Compare current subdomains with previous run to detect new assets."""
    storage_dir = os.path.join("recon_data", target_slug)
    os.makedirs(storage_dir, exist_ok=True)
    baseline_file = os.path.join(storage_dir, "baseline_subdomains.txt")
    
    previous_subdomains = set()
    if os.path.exists(baseline_file):
        with open(baseline_file, "r", encoding="utf-8") as f:
            previous_subdomains = {line.strip() for line in f if line.strip()}
            
    current_set = set(current_subdomains)
    new_assets = sorted(list(current_set - previous_subdomains))
    
    print(f"\n==========================================")
    print(f"[*] Subdomain Monitoring Delta Check")
    print(f"==========================================")
    print(f"Previous Known Assets: {len(previous_subdomains)}")
    print(f"Current Assets:        {len(current_set)}")
    
    if new_assets and previous_subdomains:
        print(f"\n[!] ALERT: {len(new_assets)} NEW ASSET(S) DETECTED!")
        for asset in new_assets[:15]:
            print(f"    --> [NEW] {asset}")
        new_file = os.path.join(storage_dir, f"new_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(new_file, "w", encoding="utf-8") as f:
            f.write("\n".join(new_assets))
        print(f"[+] Saved new assets alert to {new_file}")
    else:
        print("[+] No new assets detected since last baseline run.")
        
    # Update baseline
    with open(baseline_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(list(current_set | previous_subdomains))))
    print(f"[+] Baseline updated at {baseline_file}")
    return new_assets if previous_subdomains else current_subdomains

def check_liveness_and_ports(subdomains, max_hosts=50):
    """Probe hosts for web liveness and check common HTTP ports."""
    print(f"\n[*] Probing {min(len(subdomains), max_hosts)} hosts for alive web servers and ports...")
    alive = []
    
    for sub in subdomains[:max_hosts]:
        # Fast DNS resolve
        try:
            ip = socket.gethostbyname(sub)
        except Exception:
            continue
            
        host_info = {
            "subdomain": sub,
            "ip": ip,
            "endpoints": [],
            "tech_stack": set()
        }
        
        # Test common web ports
        for port in [443, 80, 8080, 8443]:
            proto = "https" if port in [443, 8443] else "http"
            url = f"{proto}://{sub}" if port in [80, 443] else f"{proto}://{sub}:{port}"
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=4) as resp:
                    status = resp.status
                    headers = dict(resp.getheaders())
                    body = resp.read(2048).decode('utf-8', errors='ignore')
                    
                    # Extract title
                    title_match = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE | re.DOTALL)
                    title = title_match.group(1).strip() if title_match else "No Title"
                    
                    # Tech stack detection
                    server = headers.get('server', '')
                    x_powered = headers.get('x-powered-by', '')
                    if 'cloudflare' in server.lower():
                        host_info["tech_stack"].add("Cloudflare")
                    if 'nginx' in server.lower():
                        host_info["tech_stack"].add("Nginx")
                    if 'apache' in server.lower():
                        host_info["tech_stack"].add("Apache")
                    if 'wp-' in body or 'wordpress' in body.lower():
                        host_info["tech_stack"].add("WordPress")
                    if 'swagger' in body.lower() or 'openapi' in body.lower():
                        host_info["tech_stack"].add("API Docs (Swagger)")
                        
                    endpoint_data = {
                        "url": url,
                        "port": port,
                        "status": status,
                        "title": title[:60],
                        "server": server
                    }
                    host_info["endpoints"].append(endpoint_data)
                    print(f"  [ALIVE] {url} -> HTTP {status} | Title: {title[:40]} | Tech: {list(host_info['tech_stack'])}")
            except Exception:
                pass
                
        if host_info["endpoints"]:
            host_info["tech_stack"] = list(host_info["tech_stack"])
            alive.append(host_info)
            
    print(f"[+] Total alive web hosts found: {len(alive)}")
    return alive

def capture_visual_recon(target_slug, alive_hosts, max_screenshots=20):
    """Capture headless screenshots and generate an HTML gallery for visual triage."""
    gallery_dir = os.path.join("recon_data", target_slug, "visual_gallery")
    screenshots_dir = os.path.join(gallery_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print(f"\n[*] Capturing headless visual recon screenshots with Chrome Canary...")
    captured = []
    
    for host in alive_hosts[:max_screenshots]:
        for ep in host["endpoints"]:
            url = ep["url"]
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', url.replace('https://', '').replace('http://', ''))[:60] + ".png"
            shot_path = os.path.abspath(os.path.join(screenshots_dir, safe_name))
            
            cmd = [
                CHROME_PATH,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1200,800",
                f"--screenshot={shot_path}",
                url
            ]
            try:
                subprocess.run(cmd, timeout=12, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(shot_path):
                    rel_shot = os.path.join("screenshots", safe_name)
                    captured.append({
                        "url": url,
                        "subdomain": host["subdomain"],
                        "title": ep["title"],
                        "status": ep["status"],
                        "tech": host["tech_stack"],
                        "screenshot": rel_shot
                    })
                    print(f"  [+] Captured: {url} -> {safe_name}")
            except Exception:
                pass
                
    # Generate HTML Visual Triage Report
    report_path = os.path.join(gallery_dir, "index.html")
    cards_html = ""
    for item in captured:
        tech_badges = " ".join(f'<span class="badge">{t}</span>' for t in item["tech"])
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <a href="{item['url']}" target="_blank" class="card-title">{item['url']}</a>
                <span class="status-code">HTTP {item['status']}</span>
            </div>
            <div class="card-body">
                <p class="site-title">{item['title']}</p>
                <div class="tech-tags">{tech_badges}</div>
                <div class="img-wrapper">
                    <img src="{item['screenshot']}" alt="Screenshot" loading="lazy"/>
                </div>
            </div>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Visual Recon Gallery - {target_slug}</title>
    <style>
        body {{ background-color: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 24px; }}
        h1 {{ font-size: 24px; margin-bottom: 8px; color: #38bdf8; }}
        .subtitle {{ color: #94a3b8; margin-bottom: 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 20px; }}
        .card {{ background: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }}
        .card-header {{ padding: 12px 16px; background: #0f172a; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; }}
        .card-title {{ color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 14px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 320px; }}
        .card-title:hover {{ text-decoration: underline; }}
        .status-code {{ background: #059669; color: #ecfdf5; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
        .card-body {{ padding: 16px; }}
        .site-title {{ margin: 0 0 8px 0; font-size: 13px; color: #e2e8f0; font-weight: 500; }}
        .tech-tags {{ margin-bottom: 12px; min-height: 22px; }}
        .badge {{ background: #475569; color: #f1f5f9; font-size: 11px; padding: 2px 8px; border-radius: 12px; margin-right: 4px; }}
        .img-wrapper {{ width: 100%; height: 260px; overflow: hidden; border-radius: 4px; border: 1px solid #475569; }}
        .img-wrapper img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; }}
    </style>
</head>
<body>
    <h1>Visual Recon Gallery: {target_slug}</h1>
    <div class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Visual Targets: {len(captured)}</div>
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"\n[+] Visual Recon HTML Gallery compiled successfully: {os.path.abspath(report_path)}")
    return report_path

def main():
    parser = argparse.ArgumentParser(description="3-Pillar Bug Bounty Recon Pipeline")
    parser.add_argument("domain", help="Root domain (e.g. web.com, bluehost.com)")
    parser.add_argument("--slug", help="Target slug (e.g. ONEWEB)", default=None)
    parser.add_argument("--skip-screenshots", action="store_true", help="Skip capturing visual screenshots")
    args = parser.parse_args()
    
    domain = args.domain.strip().lower()
    slug = args.slug or domain.replace('.', '_').upper()
    
    print("=" * 60)
    print(f"[*] STARTING RECON AUTOMATION PIPELINE: {domain} ({slug})")
    print("=" * 60)
    
    # Pillar 1: Subdomain Discovery & Diff Monitoring
    subs = query_crtsh(domain)
    if not subs:
        subs = [domain, f"app.{domain}", f"www.{domain}", f"api.{domain}"]
    
    active_targets = diff_monitoring(slug, subs)
    
    # Pillar 2: Smart Port Scanning & Liveness Enumeration
    alive_hosts = check_liveness_and_ports(active_targets, max_hosts=15)
    
    # Pillar 3: Visual Recon & Tech Stack Identification
    if not args.skip_screenshots and alive_hosts:
        gallery_path = capture_visual_recon(slug, alive_hosts, max_screenshots=10)
        print(f"\n[+] Recon pipeline execution completed for {domain}!")
        print(f"[+] View Gallery: file:///{gallery_path.replace(os.sep, '/')}")
    else:
        print(f"\n[+] Recon pipeline completed (Screenshots skipped).")

if __name__ == "__main__":
    main()
