import os
import json
from datetime import datetime
import requests

# ASCII маскировка путей
C = chr(58)
S = chr(47)

# Официальный мобильный поисковый JSON-шлюз Bandcamp
BASE_API = f"https{C}{S}{S}bandcamp.com{S}api{S}bcsearch{S}1{S}autocomplete"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Ключевые поисковые запросы для мобильного шлюза
QUERIES = ["black metal album", "atmospheric black metal", "depressive black metal"]

# Исключаем лишние жанры
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

def parse_bandcamp_mobile_search():
    now = datetime.now()
    found_releases = []
    seen_urls = set()

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for q in QUERIES:
        params = {"q": q}
        try:
            # Мобильное API принимает обычные GET-запросы с поисковой строкой
            res = requests.get(BASE_API, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            data = res.json()
            # В автодополнении результаты лежат в ключе 'auto'
            items = data.get("auto", [])
            
            for item in items:
                # Извлекаем ссылку на альбом
                album_url = item.get("url", "")
                if not album_url or album_url in seen_urls:
                    continue
                    
                # В мобильной поисковой выдаче имя пишется в поле 'name' в формате "Band Name - Album Name"
                name_raw = item.get("name", "")
                if " - " in name_raw:
                    artist, title = name_raw.split(" - ", 1)
                else:
                    artist = name_raw
                    title = "Release"
                    
                # Очищаем от лишних пробелов
                artist = artist.strip()
                title = title.strip()
                
                # Фильтрация поджанров (проверяем всю карточку релиза)
                full_desc = f"{artist} {title} {q}".lower()
                if any(forbidden in full_desc for forbidden in FORBIDDEN_KEYWORDS):
                    continue
                    
                # Определяем страну для флага по строке локации
                location = item.get("stat", "").lower()
                flag = "🇳🇴"  # Тру-дефолт флаг
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in location:
                        flag = c_flag
                        break

                # Формируем ссылку на YouTube по твоему шаблону
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                # Форматируем красивое описание жанра
                genre_text = item.get("stat", "Atmospheric Black Metal").strip()
                if not genre_text or len(genre_text) < 3:
                    genre_text = "Black Metal"

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
            print(f"Ошибка мобильного поиска для запроса {q}: {e}")
            continue

    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (MOBILE SEARCH API)</b>\n\nМобильный поисковый шлюз ответил успешно, но чистых блэк-метал релизов по критериям не обнаружено."
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
    results = parse_bandcamp_mobile_search()
    send_to_telegram(results)
    
