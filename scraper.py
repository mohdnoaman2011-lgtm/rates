import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def load_existing_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data and "rates" in data and len(data["rates"]) > 0:
                return data
    except Exception as e:
        print(f"Read error: {e}")
    return None

def fetch_rates_from_web():
    urls = [
        "https://sudanakhbar.com",
        "https://bazaar.sd"
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for url in urls:
        try:
            print(f"Trying {url}...")
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text(" ", strip=True)
                
                usd_match = re.search(r'(?:دولار|USD)[^\d]{0,30}(\d{4,5})', text)
                sar_match = re.search(r'(?:سعودي|SAR)[^\d]{0,30}(\d{3,4})', text)
                aed_match = re.search(r'(?:إماراتي|AED)[^\d]{0,30}(\d{3,4})', text)
                egp_match = re.search(r'(?:مصري|EGP)[^\d]{0,30}(\d{2,3})', text)
                
                if usd_match:
                    usd = int(usd_match.group(1))
                    sar = int(sar_match.group(1)) if sar_match else round(usd / 3.75)
                    aed = int(aed_match.group(1)) if aed_match else round(usd / 3.67)
                    egp = int(egp_match.group(1)) if egp_match else round(usd / 50)
                    
                    return {
                        "USD": {"buy": usd, "sell": usd + 100},
                        "SAR": {"buy": sar, "sell": sar + 30},
                        "AED": {"buy": aed, "sell": aed + 30},
                        "EGP": {"buy": egp, "sell": egp + 5}
                    }
        except Exception as e:
            print(f"Failed on {url}: {e}")
            
    return None

def main():
    new_rates = fetch_rates_from_web()
    
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "auto",
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated rates.json with live data!")
    else:
        old_data = load_existing_data()
        if old_data:
            print("WARNING: Fetch failed, keeping existing rates.")
        else:
            fallback = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "source": "fallback",
                "rates": {
                    "USD": {"buy": 12100, "sell": 12400},
                    "SAR": {"buy": 3220, "sell": 3300},
                    "AED": {"buy": 3290, "sell": 3370},
                    "EGP": {"buy": 220, "sell": 230}
                }
            }
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(fallback, f, ensure_ascii=False, indent=2)
            print("INFO: Initialized rates.json with fallback data.")

if __name__ == "__main__":
    main()
