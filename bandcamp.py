import os
import json
import requests

# ASCII маскировка
C = chr(58)
S = chr(47)

# Официальный, открытый поисковый шлюз API v1
BASE_API = f"https{C}{S}{S}bandcamp.com{S}api{S}v1{S}search"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Поисковые фразы для андеграундного блэка
SEARCH_QUERIES = [
    "black metal album",
    "atmospheric black metal",
    "depressive black metal"
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_search_api():
    found_releases = []
    seen_urls = set()
    total_search_items = 0

    for query in SEARCH_QUERIES:
        # Передаем легальные поисковые параметры
        # item_type="a" означает только АЛЬБОМЫ (Albums)
        params = {
            "q": query,
            "item_type": "a",
            "page": 1
        }
        
        try:
            res = requests.get(BASE_API, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Поиск по запросу '{query}' вернул статус {res.status_code}")
                continue
                
            data = res.json()
            # Структура ответа v1 API: список результатов лежит в ключе 'results'
            items = data.get("results", [])
            
            for item in items:
                total_search_items += 1
                
                album_url = item.get("item_url") or item.get("url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                # Получаем название и группу
                name = item.get("name", "Unknown Album").strip()
                artist = item.get("artist_name", "Unknown Artist").strip()
                
                # Жанры/теги для фильтрации
                tags_str = " ".join(item.get("tags", [])).lower()
                
                # Проверяем на чистый блэк (без трэша/дэта)
                if any(forbidden in tags_str or forbidden in name.lower() for forbidden in FORBIDDEN_KEYWORDS):
                    continue

                clean_url = album_url.split('?') if '?' in album_url else album_url
                
                found_releases.append({
                    "artist": artist,
                    "title": name,
                    "url": clean_url
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка Поискового API для запроса {query}: {e}")
            continue

    print(f"Всего альбомов обработано в поиске: {total_search_items}")
    print(f"Отобрано чистых блэк-релизов: {len(found_releases)}")
    return found_releases[:15], total_search_items

def send_to_telegram(releases, total_search):
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (SEARCH API)</b>\n\n"
        msg += f"Поисковый шлюз v1 ответил. Обработано альбомов: <code>{total_search}</code>.\n"
        msg += "Но ни один релиз не прошел строгую блэк-метал фильтрацию!"
    else:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ УЛОВ (ЧЕРЕЗ SEARCH API)</b>\n\n"
        for r in releases:
            msg += f"• <code>{r['artist']} - {r['title']}</code>\n🔗 {r['url']}\n\n"

    if not BOT_TOKEN:
        return

    telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results, raw_total = parse_bandcamp_search_api()
    send_to_telegram(results, raw_total)
    
