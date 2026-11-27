import json
import re
import requests
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def parse_price(raw_str):
    clean = re.sub(r'[^\d]', '', raw_str)
    return int(clean) if clean else None

def fetch_via_reader():
    # استخدام وسيط مجاني لتجاوز حظر المواقع وقراءة النصوص بوضوح
    targets = [
        "https://jina.ai",
        "https://jina.ai",
        "https://jina.ai"
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    for url in targets:
        try:
            print(f"Fetching: {url}")
            resp = requests.get(url, headers=headers, timeout=25)
            if resp.status_code == 200:
                text = resp.text
                
                # البحث عن سعر الدولار (4 أو 5 خانات)
                usd_match = re.search(r'(?:دولار|USD|الأمريكي)[^\d]{0,40}(\d{1,2}[,.]?\d{3})', text)
                if usd_match:
                    usd = parse_price(usd_match.group(1))
                    if usd and 2000 <= usd <= 50000:
                        sar_m = re.search(r'(?:سعودي|SAR)[^\d]{0,40}(\d{1,2}[,.]?\d{3})', text)
                        aed_m = re.search(r'(?:إماراتي|AED)[^\d]{0,40}(\d{1,2}[,.]?\d{3})', text)
                        egp_m = re.search(r'(?:مصري|EGP)[^\d]{0,40}(\d{2,4})', text)
                        
                        sar = parse_price(sar_m.group(1)) if sar_m else round(usd / 3.75)
                        aed = parse_price(aed_m.group(1)) if aed_m else round(usd / 3.67)
                        egp = parse_price(egp_m.group(1)) if egp_m else round(usd / 50)
                        
                        return {
                            "USD": {"buy": usd, "sell": usd + 150},
                            "SAR": {"buy": sar, "sell": sar + 40},
                            "AED": {"buy": aed, "sell": aed + 40},
                            "EGP": {"buy": egp, "sell": egp + 5}
                        }
        except Exception as e:
            print(f"Error on {url}: {e}")
            
    return None

def main():
    new_rates = fetch_via_reader()
    
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "auto",
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated with live rates!")
    else:
        print("WARNING: Keeping existing rates.")

if __name__ == "__main__":
    main()
