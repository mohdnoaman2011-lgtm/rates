import json
import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def normalize_digits(text):
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    return text.translate(str.maketrans(arabic_digits, english_digits))

def parse_price(raw_str):
    clean = re.sub(r'[^\d]', '', raw_str)
    return int(clean) if clean else None

def fetch_rates():
    base_url = "https://news.google.com/rss/search"
    queries = [
        "سعر الدولار في السودان اليوم السوق الموازي",
        "أسعار العملات في السودان اليوم السوق الأسود"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_texts = []
    for q in queries:
        query_params = {
            "q": q,
            "hl": "ar",
            "gl": "SD",
            "ceid": "SD:ar"
        }
        try:
            resp = requests.get(base_url, params=query_params, headers=headers, timeout=20)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item')[:15]:
                    t = item.find('title').text if item.find('title') is not None else ""
                    d = item.find('description').text if item.find('description') is not None else ""
                    clean_item = BeautifulSoup(f"{t} {d}", 'html.parser').get_text(" ")
                    all_texts.append(normalize_digits(clean_item))
        except Exception as e:
            print("Error:", e)

    full_text = " | ".join(all_texts)
    
    # استخراج جميع الأرقام من 4 أو 5 خانات
    matches = re.findall(r'\b(\d{1,2}[,.]?\d{3})\b', full_text)
    excluded = {2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028}
    valid_usd = []
    
    for m in matches:
        val = parse_price(m)
        if val and 3500 <= val <= 35000 and val not in excluded:
            valid_usd.append(val)
            
    print("All extracted numbers:", valid_usd)
    
    if valid_usd:
        # إذا وجدنا أرقاماً في نطاق 10000 فما فوق نأخذها، وإلا نأخذ أعلى رقم متاح
        high_rates = [v for v in valid_usd if v >= 10000]
        if high_rates:
            usd = max(set(high_rates), key=high_rates.count)
        else:
            usd = max(valid_usd)
            
        sar = round(usd / 3.75)
        aed = round(usd / 3.67)
        egp = round(usd / 50)
        
        return {
            "USD": {"buy": usd, "sell": usd + 200},
            "SAR": {"buy": sar, "sell": sar + 50},
            "AED": {"buy": aed, "sell": aed + 50},
            "EGP": {"buy": egp, "sell": egp + 5}
        }
        
    return None

def main():
    new_rates = fetch_rates()
    
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "auto",
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated rates.json!")
    else:
        print("WARNING: No numbers matched, keeping existing data.")

if __name__ == "__main__":
    main()
