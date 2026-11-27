import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def parse_price(raw_str):
    clean = re.sub(r'[^\d]', '', raw_str)
    return int(clean) if clean else None

def fetch_from_search():
    # البحث المباشر عن أحدث أخبار سعر الدولار في السوق الموازي في السودان
    url = "https://duckduckgo.com"
    payload = {'q': 'سعر الدولار في السودان اليوم السوق الموازي'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            snippets = [s.get_text(" ", strip=True) for s in soup.find_all('a', class_='result__snippet')]
            full_text = " ".join(snippets)
            print("Extracted snippets sample:", full_text[:200])
            
            # البحث عن جميع الأرقام المنطقية لسعر الدولار (من 2500 إلى 50000) في المقتطفات
            matches = re.findall(r'\b(\d{1,2}[,.]?\d{3})\b', full_text)
            valid_usd = []
            for m in matches:
                val = parse_price(m)
                # استبعاد السنوات مثل 2024, 2025, 2026
                if val and 2500 <= val <= 50000 and val not in:
                    valid_usd.append(val)
            
            if valid_usd:
                # أخذ السعر الأكثر تكراراً أو المتوسط
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
        print(f"Search fetch error: {e}")
        
    return None

def main():
    new_rates = fetch_from_search()
    
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "auto",
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated with live search rates!")
    else:
        print("WARNING: No valid rates found, keeping existing data.")

if __name__ == "__main__":
    main()
