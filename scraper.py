import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

JSON_FILE = 'rates.json'

def load_existing_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"last_updated": "", "rates": {}}

def fetch_rates():
    # رابط مثال لأحد مواقع الرصد (يجب تعديل محددات HTML حسب الموقع الفعلي)
    url = "https://alsoug.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ملاحظة: هنا يتم استخراج الأرقام من وسوم HTML الخاصة بالموقع
        # كمثال هيكلي للبيانات التي ستعود:
        new_rates = {
            "USD": {"buy": 12100, "sell": 12400},
            "SAR": {"buy": 3220, "sell": 3300},
            "AED": {"buy": 3290, "sell": 3370},
            "EGP": {"buy": 220, "sell": 230}
        }
        return new_rates
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    old_data = load_existing_data()
    new_rates = fetch_rates()
    
    # تحديث الملف فقط في حال نجاح الجلب ووجود بيانات صحيحة
    if new_rates:
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "rates": new_rates
        }
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("Rates updated successfully.")
    else:
        print("Keeping old rates due to fetch failure.")

if __name__ == "__main__":
    main()
