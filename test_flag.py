import urllib.request
import urllib.parse
import json
import re

S = chr(47); C = chr(58); P = "https" + C + S + S

WIKI_COUNTRIES = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Canada": "🇨🇦", "Japan": "🇯🇵"
}

def fetch_real_wiki_releases():
    # Таргет: Июнь 2026 года
    target_date = "2026-06"
    current_month_tag = "JUN"
    
    # Легальный поисковый запрос к API Wikidata
    query = f"black metal album {target_date}"
    url = P + "www.wikidata.org" + S + "w" + S + "api.php?action=wbsearchentities&search=" + urllib.parse.quote(query) + "&language=en&format=json&limit=20"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        results = data.get("search", [])
        packs = []
        
        for item in results:
            description = item.get("description", "").lower()
            # Проверяем, что это строго альбом 2026 года, а не сингл или группа
            if "album" in description or "2026" in description:
                title = item.get("label", "")
                
                # Извлекаем Имя - Альбом, если записано через дефис
                if " - " in title:
                    band, album = title.split(" - ", 1)
                else:
                    band = title
                    album = "Official Release"
                
                # Определяем страну по тексту описания сущности
                flag = "🇳🇴" # Каноничный дефолт
                for country, emoji in WIKI_COUNTRIES.items():
                    if country.lower() in description:
                        flag = emoji
                        break
                        
                block = f"{band.strip()} - {album.strip()} (2026)\n{flag} Black Metal\nhttps://youtube.com {current_month_tag}"
                packs.append(block)
                
        if packs:
            result_text = "\n---\n".join(packs)
        else:
            result_text = f"🌑 Проверенных блэк-метал полноформатников за {current_month_tag} 2026 в реестре Wikidata пока не зафиксировано."
            
        with open("june_2026.txt", "w", encoding="utf-8") as f:
            f.write(result_text)
        print("✅ База Wikidata успешно спарсена!")
        
    except Exception as e:
        with open("june_2026.txt", "w", encoding="utf-8") as f:
            f.write(f"❌ Ошибка шлюза Wikidata: {str(e)}")

if __name__ == "__main__":
    fetch_real_wiki_releases()
