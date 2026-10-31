import urllib.request
import re
import json

def fetch_and_analyze(url, label):
    print(f"\n=== Analyzing {label} ({url}) ===")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            print(f"Downloaded {len(data)} bytes")
            
            # Find URLs
            urls = set(re.findall(r'https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9_./?%&=-]*)?', data))
            print(f"Discovered {len(urls)} external/internal URLs:")
            for u in sorted(urls):
                if any(domain in u for domain in ['web.com', 'builderservices', 'newfold', 'azure', 'blob', 'mywebsitebuilder', 'ecomdash']):
                    print("  *", u)
                    
            # Find API routes
            routes = set(re.findall(r'["\'](/api/[a-zA-Z0-9_/-]+|/v[0-9]/[a-zA-Z0-9_/-]+)["\']', data))
            if routes:
                print(f"Discovered {len(routes)} API routes:")
                for r in sorted(routes)[:20]:
                    print("  ->", r)
    except Exception as e:
        print(f"Error fetching {url}: {e}")

if __name__ == '__main__':
    fetch_and_analyze('https://app.web.com/ai/174/main.bundle.js', 'AI Bundle')
    fetch_and_analyze('https://app.web.com/aiimagegenerator/49/main.bundle.js', 'AI DALL-E Image Generator Bundle')
    fetch_and_analyze('https://app.web.com/account/2556/app-config.js?hash=2556', 'Account Settings Config')
