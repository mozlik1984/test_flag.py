import os
import json
from datetime import datetime
import requests

# Защита строк через ASCII-коды
C = chr(58)
S = chr(47)

# Мобильный эндпоинт Bandcamp
BASE_API = f"https{C}{S}{S}bandcamp.com{S}api{S}hub{S}2{S}dig_deeper"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Список целевых поджанров Блэк-метала
BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_TAGS = ["thrash-metal", "death-metal", "heavy-metal", "power-metal", "metalcore"]

# Маскируемся под официальное мобильное приложение Bandcamp для Android
HEADERS = {
    "User-Agent": "Bandcamp/3.4.0 (Linux; Android 13; Build/TP1A.220624.014) Mobile/App",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def parse_bandcamp_mobile_api():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    total_items = 0

    for tag in BLACK_METAL_TAGS:
        payload = {
            "tag": tag,
            "sort_key": "date",
            "page": 0
        }
        
        try:
            res = requests.post(BASE_API, json=payload, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Шлюз {tag} вернул статус {res.status_code}")
                continue
                
            data = res.json()
            items = data.get("items", []) or data.get("results", [])
            
            for item in items:
                total_items += 1
                album_url = item.get("tralbum_url") or item.get("url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                item_tags = [t.lower() for t in item.get("tags", [])]
                if any(forbidden in item_tags for forbidden in FORBIDDEN_TAGS):
                    continue
                
                rel_date_str = item.get("release_date") or item.get("publish_date")
                is_target_period = False
                
                if rel_date_str:
                    try:
                        if "-" in rel_date_str:
                            rel_date = datetime.strptime(rel_date_str[:10], "%Y-%m-%d")
                        else:
                            rel_date = datetime.strptime(rel_date_str, "%d %b %Y")
                        
                        # Заменили "in" на "> 6", чтобы телефон не воровал скобки!
                        if rel_date.year == 2026 and rel_date.month > 6:
                            is_target_period = True
                    except Exception:
                        is_target_period = True
                else:
                    is_target_period = True

                if is_target_period:
                    clean_url = album_url.split('?') if '?' in album_url else album_url
                    found_releases.append({
                        "artist": item.get("artist", "Unknown Artist").strip(),
                        "title": item.get("title", "Unknown Album").strip(),
                        "url": clean_url
                    })
                    seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка мобильного API для тега {tag}: {e}")
            continue

    print(f"Всего элементов выдал мобильный шлюз: {total_items}")
    print(f"Отобрано релизов (Июль-Август): {len(found_releases)}")
    return found_releases[:15], total_items

def send_to_telegram(releases, total_items):
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (MOBILE API)</b>\n\n"
        msg += f"Запрос прошел успешно! Элементов в обработке: <code>{total_items}</code>.\n"
        msg += "Но подходящих релизов за Июль или Август 2026 не найдено."
    else:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ УЛОВ (ОБКАТКА: ИЮЛЬ-АВГУСТ 2026)</b>\n\n"
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
    results, raw_total = parse_bandcamp_mobile_api()
    send_to_telegram(results, raw_total)
    
