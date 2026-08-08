import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка
C = chr(58)
S = chr(47)

# Неблокируемый шлюз встроенных плееров Bandcamp
BASE_PLAYER = f"https{C}{S}{S}bandcamp.com{S}EmbeddedPlayer"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_embedded():
    found_releases = []
    seen_urls = set()
    total_parsed_items = 0

    for tag in BLACK_METAL_TAGS:
        # Запрашиваем верстку встроенного плеера для конкретного тега
        params = {"tag": tag, "v": "2"}
        try:
            res = requests.get(BASE_PLAYER, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Шлюз виджетов для тега {tag} вернул статус {res.status_code}")
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Внутри HTML-плеера все альбомы лежат в простых и понятных блоках с классом visual
            artworks = soup.find_all("div", class_="visual") or soup.find_all("a", class_="art-link")
            
            for art in artworks:
                total_parsed_items += 1
                
                # Ищем ссылку на альбом
                link_tag = art if art.name == "a" else art.find("a", href=True)
                if not link_tag or not link_tag.has_attr("href"):
                    continue
                    
                album_url = link_tag["href"]
                if album_url in seen_urls:
                    continue
                    
                # Ищем текстовый блок с описанием альбома
                # Во встроенных плеерах название пишется на виду внутри атрибутов или соседних тегов
                title_tag = art.find("img")
                album_info = title_tag.get("alt", "") if title_tag else ""
                
                if " by " in album_info:
                    title, artist = album_info.split(" by ", 1)
                else:
                    title, artist = album_info, "Unknown Underground Artist"
                    
                # Проверяем на жесткие блэк-метал исключения
                if any(forbidden in album_info.lower() for forbidden in FORBIDDEN_KEYWORDS):
                    continue

                clean_url = album_url.split('?') if '?' in album_url else album_url
                
                if title.strip() and title.strip() != "Unknown Album":
                    found_releases.append({
                        "artist": artist.strip(),
                        "title": title.strip(),
                        "url": clean_url
                    })
                    seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка парсинга виджета для тега {tag}: {e}")
            continue

    print(f"Всего элементов выдал шлюз виджетов: {total_parsed_items}")
    print(f"Отобрано чистых релизов блэка: {len(found_releases)}")
    return found_releases[:15], total_parsed_items

def send_to_telegram(releases, total_items):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (EMBEDDED SHIELD)</b>\n\n"
        msg += f"Шлюз встроенных плееров открыт! Обработано элементов: <code>{total_items}</code>.\n"
        msg += "Но карточки альбомов внутри виджета пустые или заблокированы."
    else:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ УЛОВ (ЧЕРЕЗ EMBEDDED PLAYER) ({months_ru[now.month]} {now.year})</b>\n\n"
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
    results, raw_total = parse_bandcamp_embedded()
    send_to_telegram(results, raw_total)
    
