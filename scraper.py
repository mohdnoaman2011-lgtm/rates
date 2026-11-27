import json
import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def load_existing_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data and "rates" in data and len(data["rates"]) > 0:
                return data
    except:
        pass
    return None

def parse_price(raw_str):
    # إزالة الفواصل والمسافات وتحويل النص لرقم صحيح
    clean = re.sub(r'[^\d]', '', raw_str)
    return int(clean) if clean else None

def fetch_rates_from_rss():
    # خلاصات RSS مفتوحة ومستقرة للمواقع الإخبارية السودانية
    rss_urls = [
        "https://sudanakhbar.com",
        "https://altaghyeer.info"
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; CurrencyBot/1.0)'
    }
    
    for url in rss_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item'):
                    title = item.find('title').text or ""
                    desc = item.find('description').text or ""
                    full_text = BeautifulSoup(title + " " + desc, 'html.parser').get_text(" ")
                    
                    # التحقق من أن الخبر يتحدث عن أسعار العملات
                    if any(w in full_text for w in ['سعر', 'أسعار', 'الدولار', 'الصرف', 'الموازي']):
                        # البحث عن رقم من 4 أو 5 خانات (مع أو بدون فاصلة) بجانب كلمة دولار
                        usd_match = re.search(r'(?:دولار|USD)[^\d]{0,35}(\d{1,2}[,.]?\d{3})', full_text)
                        if usd_match:
                            usd = parse_price(usd_match.group(1))
                            # التأكد من أن الرقم منطقي (بين 2000 و 50000)
                            if usd and 2000 <= usd <= 50000:
                                sar_m = re.search(r'(?:سعودي|SAR)[^\d]{0,35}(\d{1,2}[,.]?\d{3})', full_text)
                                aed_m = re.search(r'(?:إماراتي|AED)[^\d]{0,35}(\d{1,2}[,.]?\d{3})', full_text)
                                egp_m = re.search(r'(?:مصري|EGP)[^\d]{0,35}(\d{2,4})', full_text)
                                
                                sar = parse_price(sar_m.group(1)) if sar_m else round(usd / 3.75)
                                aed = parse_price(aed_m.group(1)) if aed_m else round(usd / 3.67)
                                egp = parse_price(egp_m.group(1)) if egp_m else round(usd / 50)
                                
                                return {
                                    "USD": {"buy": usd, "sell": usd + 100},
                                    "SAR": {"buy": sar, "sell": sar + 30},
                                    "AED": {"buy": aed, "sell": aed + 30},
                                    "EGP": {"buy": egp, "sell": egp + 5}
                                }
        except Exception as e:
            print(f"RSS error on {url}: {e}")
            
    return None

def main():
    new_rates = fetch_rates_from_rss()
    
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "auto",
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated with live RSS rates!")
    else:
        print("WARNING: Could not find new rates in RSS, keeping existing data.")

if __name__ == "__main__":
    main()
