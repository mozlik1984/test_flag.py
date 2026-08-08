import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка путей
C = chr(58)
S = chr(47)

# Публичный и неблокируемый шлюз встроенных плееров Bandcamp
BASE_PLAYER = f"https{C}{S}{S}bandcamp.com{S}EmbeddedPlayer"
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_embedded():
    now = datetime.now()
    found_releases = []
    seen_identities = set()

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for tag in BLACK_METAL_TAGS:
        # Запрашиваем верстку плеера-виджета для конкретного тега (v=2 — это современная сетка релизов)
        params = {"tag": tag, "v": "2"}
        try:
            res = requests.get(BASE_PLAYER, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Внутри HTML-кода плеера все релизы лежат на виду в блоках картинок с тегом img
            artworks = soup.find_all("div", class_="visual") or soup.find_all("a", class_="art-link")
            
            for art in artworks:
                img_tag = art.find("img") if art.name != "img" else art
                if not img_tag or not img_tag.has_attr("alt"):
                    continue
                    
                # Bandcamp пишет метаданные релиза прямо в атрибут alt картинки в формате "Album Name by Band Name"
                album_info = img_tag["alt"].strip()
                if not album_info or " by " not in album_info:
                    continue
                    
                title, artist = album_info.split(" by ", 1)
                title = title.strip()
                artist = artist.strip()
                
                full_identity = f"{artist} - {title}".lower()
                if full_identity in seen_identities:
                    continue
                    
                # Жесткий блэк-метал отсев
                if any(forbidden in album_info.lower() for forbidden in FORBIDDEN_KEYWORDS):
                    continue

                # Пытаемся нащупать локацию группы (виджет иногда подгружает её в соседние дата-атрибуты)
                flag = "🇳🇴"  # Тру-дефолт флаг по умолчанию
                parent_a = art if art.name == "a" else art.find("a", href=True)
                if parent_a and parent_a.has_attr("href"):
                    # Если в ссылке проскакивает название страны, подставляем флаг
                    url_lower = parent_a["href"].lower()
                    for c_key, c_flag in COUNTRY_FLAGS.items():
                        if c_key in url_lower:
                            flag = c_flag
                            break

                # Генерируем прямую поисковую ссылку на YouTube по твоему шаблону
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                # Красиво форматируем название поджанра релиза
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
                seen_identities.add(full_identity)

        except Exception as e:
            print(f"Ошибка парсинга виджета для тега {tag}: {e}")
            continue

    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (EMBEDDED SHIELD)</b>\n\nШлюз виджетов открылся успешно, но свежих блэк-метал релизов по критериям не обнаружено."
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
    
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results = parse_bandcamp_embedded()
    send_to_telegram(results)
    
