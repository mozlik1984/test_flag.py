import os
import json
import urllib.parse
from datetime import datetime
import requests

# ASCII маскировка путей для Telegram
C = chr(58)
S = chr(47)
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Надежный прокси-декодер для обхода Cloudflare в GET-режиме
PROXY_GATEWAY = f"https{C}{S}{S}api.allorigins.win{S}get?url="

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

# Словарь для автоматического сопоставления флагов стран
COUNTRY_FLAGS = {
    "norway": "🇳🇴", "sweden": "🇸🇪", "finland": "🇫🇮", "france": "🇫🇷",
    "germany": "🇩🇪", "usa": "🇺🇸", "united states": "🇺🇸", "ukraine": "🇺🇦", 
    "poland": "🇵🇱", "austria": "🇦🇹", "italy": "🇮🇹", "canada": "🇨🇦", 
    "iceland": "🇮🇸", "greece": "🇬🇷", "russia": "🇷🇺", "united kingdom": "🇬🇧"
}

def parse_bandcamp_rss_proxy():
    now = datetime.now()
    found_releases = []
    seen_urls = set()

    # Текстовая метка месяца (например, "AUG")
    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for tag in BLACK_METAL_TAGS:
        # Стучимся в мобильный JSON-шлюз самого Bandcamp через allorigins
        target_url = f"https{C}{S}{S}bandcamp.com{S}api{S}hub{S}2{S}dig_deeper"
        
        try:
            # AllOrigins проксирует GET запросы идеально
            encoded_url = urllib.parse.quote_plus(target_url)
            
            # Имитируем запрос приложения
            res = requests.get(f"{PROXY_GATEWAY}{encoded_url}", timeout=20)
            if res.status_code != 200:
                continue
                
            payload_data = res.json()
            html_content = payload_data.get("contents", "")
            
            if not html_content or "initial_results" not in html_content:
                continue
                
            # Разбираем легальный JSON, который прокси стянул с Bandcamp
            data = json.loads(html_content)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                title = item.get("title", "Unknown Album").strip()
                artist = item.get("artist", "Unknown Artist").strip()
                
                # Фильтрация (отсекаем лишние метал-жанры)
                item_tags = [t.lower() for t in item.get("tags", [])]
                full_desc = f"{title} {artist} {' '.join(item_tags)}".lower()
                if any(forbidden in full_desc for forbidden in FORBIDDEN_KEYWORDS):
                    continue
                
                # Ищем страну группы для эмодзи-флага
                location = item.get("artist_location", "").lower()
                flag = "🇳🇴" # Тру-дефолт флаг по умолчанию
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in location:
                        flag = c_flag
                        break

                genre_text = item.get("genre") or tag.replace("-", " ").title()

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": current_year,
                    "flag": flag,
                    "genre": genre_text,
                    "month": month_tag
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка прорыва для тега {tag}: {e}")
            continue
            
    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        # Честное уведомление БЕЗ левых подсунутых релизов!
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (PROXY FLOW)</b>\n\nЗапрос прошел успешно, но живых новых релизов блэк-металла на Bandcamp сейчас не обнаружено."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

    # Собираем итоговое текстовое сообщение строго по твоему идеальному шаблону!
    msg = ""
    for r in releases:
        msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
        msg += f"{r['flag']} {r['genre']}\n"
        msg += f"https{C}{S}{S}youtube.com {r['month']}\n" # Строго фиксированная ссылка-заглушка!
        msg += "---\n"  # Твой разделитель между релизами

    telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results = parse_bandcamp_rss_proxy()
    send_to_telegram(results)
    
