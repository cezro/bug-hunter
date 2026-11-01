import urllib.request
import re
import json
import xml.etree.ElementTree as ET
import html as html_lib

video_id = 'Kg09aktVJL4'
url = f'https://www.youtube.com/watch?v={video_id}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

try:
    with urllib.request.urlopen(req) as resp:
        page_html = resp.read().decode('utf-8', errors='ignore')
        
    match = re.search(r'"captionTracks":\s*(\[.*?\])', page_html)
    if match:
        tracks = json.loads(match.group(1))
        for t in tracks:
            if "en" in t.get("languageCode", ""):
                base_url = t.get("baseUrl")
                print("Fetching from:", base_url[:80])
                cap_req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(cap_req) as cap_resp:
                    content = cap_resp.read().decode('utf-8', errors='ignore')
                    print("Raw length:", len(content))
                    # Parse XML timedtext
                    root = ET.fromstring(content)
                    texts = []
                    for elem in root.findall(".//text"):
                        if elem.text:
                            texts.append(html_lib.unescape(elem.text.strip()))
                    full_transcript = " ".join(texts)
                    print(f"\n[+] Extracted Full Transcript ({len(full_transcript)} chars, {len(texts)} lines):")
                    with open("evidence/youtube_transcript.txt", "w", encoding="utf-8") as f:
                        f.write(full_transcript)
                    print("[+] Saved to evidence/youtube_transcript.txt")
                    print("\nFirst 600 characters:")
                    print(full_transcript[:600])
                    break
except Exception as e:
    import traceback
    traceback.print_exc()
