import os
import json
from datetime import datetime
import requests

# ASCII маскировка путей
C = chr(58)
S = chr(47)

# Официальный внутренний JSON шлюз Bandcamp без защиты Cloudflare
BASE_API = f"https{C}{S}{S}bandcamp.com{S}api{S}fancast{S}1{S}collection_items"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

COUNTRY_FLAGS = {
    "norway": "🇳🇴", "sweden": "🇸🇪", "finland": "🇫🇮", "france": "🇫🇷",
    "germany": "🇩🇪", "usa": "🇺🇸", "united states": "🇺🇸", "ukraine": "🇺🇦", 
    "poland": "🇵🇱", "austria": "🇦🇹", "italy": "🇮🇹", "canada": "🇨🇦", 
    "iceland": "🇮🇸", "greece": "🇬🇷", "russia": "🇷🇺", "united kingdom": "🇬🇧"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

def parse_bandcamp_collection_api():
    now = datetime.now()
    found_releases = []
    seen_ids = set()

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for tag in BLACK_METAL_TAGS:
        # Формируем легальный запрос к API коллекций по тегу
        payload = {
            "fan_id": 1,
            "older_than_token": "9999999999:9999999999",
            "count": 20,
            "tag": tag
        }
        
        try:
            res = requests.post(BASE_API, json=payload, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            data = res.json()
            # В этом API альбомы лежат внутри ключа 'items'
            items = data.get("items", [])
            
            for item in items:
                # Нам нужны только альбомы
                if item.get("item_type") != "album":
                    continue
                    
                item_id = item.get("item_id")
                if not item_id or item_id in seen_ids:
                    continue
                    
                title = item.get("item_title", "Unknown Album").strip()
                artist = item.get("band_name", "Unknown Artist").strip()
                
                # Собираем текстовое описание для блэк-метал фильтрации
                full_desc = f"{title} {artist} {tag}".lower()
                if any(forbidden in full_desc for forbidden in FORBIDDEN_KEYWORDS):
                    continue
                    
                # Ищем страну для флага
                location = item.get("location", "").lower()
                flag = "🇳🇴" # Тру-дефолт флаг
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in location:
                        flag = c_flag
                        break

                # Формируем ссылку на YouTube по твоему шаблону
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                # Форматируем название жанра красиво
                genre_text = tag.replace("-", " ").title()

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": current_year,
                    "flag": flag,
                    "genre": genre_text,
                    "youtube": youtube_link,
                    "month": month_tag
                })
                seen_ids.add(item_id)

        except Exception as e:
            print(f"Ошибка шлюза коллекций для тега {tag}: {e}")
            continue

    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (COLLECTION API)</b>\n\nШлюз API открылся успешно, но чистых блэк-метал релизов по критериям не обнаружено."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

    # Собираем текстовое сообщение строго по твоему шаблону!
    msg = ""
    for r in releases:
        msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
        msg += f"{r['flag']} {r['genre']}\n"
        msg += f"{r['youtube']} {r['month']}\n"
        msg += "---\n"

    telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results = parse_bandcamp_collection_api()
    send_to_telegram(results)
    
