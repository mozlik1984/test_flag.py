import os
import json
from datetime import datetime
import requests
import cloudscraper
from bs4 import BeautifulSoup

# ASCII маскировка путей
C = chr(58)
S = chr(47)

# Прямой базовый URL Bandcamp
BASE_BC = f"https{C}{S}{S}bandcamp.com{S}tag{S}"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

# Словарь для автоматической расстановки флагов стран по локации группы
COUNTRY_FLAGS = {
    "norway": "🇳🇴", "sweden": "🇸🇪", "finland": "🇫🇮", "france": "🇫🇷",
    "germany": "🇩🇪", "usa": "🇺🇸", "united states": "🇺🇸", "ukraine": "🇺🇦", 
    "poland": "🇵🇱", "austria": "🇦🇹", "italy": "🇮🇹", "canada": "🇨🇦", 
    "iceland": "🇮🇸", "greece": "🇬🇷", "russia": "🇷🇺", "united kingdom": "🇬🇧"
}

def parse_bandcamp_hardcore():
    now = datetime.now()
    found_releases = []
    seen_urls = set()

    # Формируем текстовую метку текущего месяца (например, "AUG")
    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    # Создаем умный сканер Cloudflare, который прикидывается браузером Chrome на Windows
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

    for tag in BLACK_METAL_TAGS:
        url = f"{BASE_BC}{tag}"
        try:
            # Стучимся напрямую на Bandcamp сквозь Cloudflare защита
            res = scraper.get(url, timeout=25)
            if res.status_code != 200:
                print(f"Защита не пробита для тега {tag}: статус {res.status_code}")
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            pagedata_tag = soup.find("div", id="pagedata") or soup.find("script", {"id": "pagedata"})
            if not pagedata_tag:
                continue
                
            raw_blob = pagedata_tag.get("data-blob") or pagedata_tag.text
            if not raw_blob:
                continue
                
            data = json.loads(raw_blob)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                title = item.get("title", "Unknown Album").strip()
                artist = item.get("artist", "Unknown Artist").strip()
                
                # Полное описание жанров релиза для жесткого отсева
                item_tags = [t.lower() for t in item.get("tags", [])]
                genre_text = item.get("genre") or tag.replace("-", " ").title()
                
                # Проверяем, чтобы в тегах и названии не было трэша/дэта/панка
                full_desc_lower = f"{title} {artist} {' '.join(item_tags)}".lower()
                if any(forbidden in full_desc_lower for forbidden in FORBIDDEN_KEYWORDS):
                    continue
                
                # Определяем страну для эмодзи-флага
                location = item.get("artist_location", "").lower()
                flag = "🇳🇴" # Тру-дефолт флаг по умолчанию
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in location:
                        flag = c_flag
                        break

                # Генерируем прямую поисковую ссылку на YouTube по твоему шаблону
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": current_year,
                    "flag": flag,
                    "genre": genre_text,
                    "youtube": youtube_link,
                    "month": month_tag
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка сканирования тега {tag}: {e}")
            continue
            
    print(f"Успешно прошло блэк-метал очистку: {len(found_releases)}")
    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (HARDCORE MODE)</b>\n\nЧерез cloudscraper зашли успешно, но свежих блэк-метал релизов на главной странице тегов сейчас нет."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

    # Собираем итоговое текстовое сообщение строго по твоему шаблону!
    msg = ""
    for r in releases:
        msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
        msg += f"{r['flag']} {r['genre']}\n"
        msg += f"{r['youtube']} {r['month']}\n"
        msg += "---\n"  # Твой разделитель между релизами

    telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    # ИСПРАВЛЕНО: Теперь requests официально импортирован на строке 4 и отработает штатно!
    res = requests.post(telegram_url, json=payload)
    if res.status_code == 200:
        print("Результат успешно отправлен в Telegram!")
    else:
        print(f"Ошибка отправки в TG: {res.status_code} - {res.text}")

if __name__ == "__main__":
    results = parse_bandcamp_hardcore()
    send_to_telegram(results)
    
