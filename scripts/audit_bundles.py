import urllib.request
import re
import json

base_url = "https://app.web.com"
targets = [
    ("/wb4wp/debug/476/main.bundle.js", "Debug Module"),
    ("/aidomaingenerator/1445/main.bundle.js", "AI Domain Generator (Public)"),
    ("/auth/1268/main.bundle.js", "Auth / Login Module"),
    ("/code-editor/44/main.bundle.js", "Code Editor Module"),
    ("/ecom/orders/main.bundle.js?hash=3686", "Store Orders Module"),
    ("/ecom/products/7129/main.bundle.js", "Store Products Module")
]

def analyze_bundle(path, label):
    url = base_url + path
    print(f"\n==========================================")
    print(f"Auditing {label}: {url}")
    print(f"==========================================")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            print(f"Size: {len(text):,} bytes")
            
            # Find URLs
            urls = set(re.findall(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_./?%&=-]*)?', text))
            internal_urls = [u for u in urls if any(d in u for d in ['web.com', 'builderservices', 'newfold', 'azure', 'blob', 'ecomdash'])]
            if internal_urls:
                print(f"[+] Internal URLs ({len(internal_urls)}):")
                for u in sorted(internal_urls)[:15]:
                    print("    ", u)
            
            # Find HTTP API paths
            api_paths = set(re.findall(r'["\'](/(?:api|v[0-9]|auth|connect|ecom|debug|user|account)/[a-zA-Z0-9_/-]+)["\']', text))
            if api_paths:
                print(f"[+] API Paths ({len(api_paths)}):")
                for p in sorted(api_paths)[:20]:
                    print("    ", p)
                    
            # Check for potential secrets, keys, debug flags
            secrets = set(re.findall(r'["\']([a-zA-Z0-9_]*(?:key|secret|token|password|auth|jwt)[a-zA-Z0-9_]*)["\']\s*:\s*["\']([^"\']{8,})["\']', text, re.IGNORECASE))
            if secrets:
                print(f"[!] Potential Keys / Config Secrets ({len(secrets)}):")
                for k, v in list(secrets)[:10]:
                    if not any(ign in k.lower() for ign in ['type', 'schema', 'action', 'label']):
                        print(f"     {k} = {v[:40]}...")

    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == '__main__':
    for p, l in targets:
        analyze_bundle(p, l)
