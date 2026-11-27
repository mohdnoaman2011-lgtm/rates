import json
import re
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def parse_price(raw_str):
    clean = re.sub(r'[^\d]', '', raw_str)
    return int(clean) if clean else None

def fetch_from_google_news():
    # البحث عبر خلاصة أخبار جوجل المفتوحة (لا تحظر خوادم GitHub أبداً)
    query = urllib.parse.quote('سعر الدولار في السودان اليوم السوق الموازي')
    url = f"https://google.com{query}&hl=ar&gl=SD&ceid=SD:ar"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://google.com)'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            titles = []
            for item in root.findall('.//item')[:15]:
                title_el = item.find('title')
                if title_el is not None and title_el.text:
                    titles.append(title_el.text)
            
            full_text = " | ".join(titles)
            print("Fetched headlines:", full_text[:300])
            
            # استخراج الأرقام من عناوين الأخبار (مثل 12100 أو 12,100 أو 12.100)
            matches = re.findall(r'\b(\d{1,2}[,.]?\d{3})\b', full_text)
            excluded = {2023, 2024, 2025, 2026, 2027}
            valid_usd = []
            
            for m in matches:
                val = parse_price(m)
                if val and 3000 <= val <= 50000 and val not in excluded:
                    valid_usd.append(val)
            
            if valid_usd:
                # اختيار السعر الأكثر تكراراً في عناوين الأخبار الحديثة
                usd = max(set(valid_usd), key=valid_usd.count)
                sar = round(usd / 3.75)
                aed = round(usd / 3.67)
                egp = round(usd / 50)
                
                return {
                    "USD": {"buy": usd, "sell": usd + 150},
                    "SAR": {"buy": sar, "sell": sar + 40},
                    "AED": {"buy": aed, "sell": aed + 40},
                    "EGP": {"buy": egp, "sell": egp + 5}
                }
    except Exception as e:
        print(f"Google News RSS error: {e}")
        
    return None

def main():
    new_rates = fetch_from_google_news()
    
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "auto",
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated with live Google News rates!")
    else:
        print("WARNING: No valid rates found, keeping existing data.")

if __name__ == "__main__":
    main()
