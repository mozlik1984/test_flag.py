import os
import json
from datetime import datetime
import requests

# ASCII маскировка
C = chr(58)
S = chr(47)

# Официальный и стабильный поисковый шлюз Discogs
BASE_DISCOGS = f"https{C}{S}{S}://discogs.com{S}database{S}search"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Жанровые фильтры Discogs
TARGET_STYLE = "Black Metal"
FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/vnd.discogs.v2.html+json"
}

def parse_via_music_index():
    now = datetime.now()
    found_releases = []
    seen_titles = set()
    total_index_items = 0

    # Будем искать релизы за текущий 2026 год
    params = {
        "style": TARGET_STYLE,
        "type": "release",
        "year": str(now.year),
        "per_page": 50,
        "page": 1
    }
    
    try:
        res = requests.get(BASE_DISCOGS, params=params, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"Шлюз музыкального индекса вернул статус {res.status_code}")
            return [], 0
            
        data = res.json()
        items = data.get("results", [])
        
        for item in items:
            total_index_items += 1
            
            # Извлекаем метаданные релиза
            full_title = item.get("title", "Unknown - Unknown") # Обычно в формате "Artist - Album"
            styles = [s.lower() for s in item.get("style", [])]
            
            if full_title in seen_titles:
                continue

            # Жесткий блэк-метал фильтр: отсекаем трэш, дез и хэви
            if any(forbidden in styles or forbidden in full_title.lower() for forbidden in FORBIDDEN_KEYWORDS):
                continue
                
            # Разбираем исполнителя и альбом
            if " - " in full_title:
                artist, title = full_title.split(" - ", 1)
            else:
                artist, title = "Underground Artist", full_title

            # Генерируем прямую поисковую ссылку на Bandcamp, так как Discogs точно знает названия альбомов
            # Это легальный способ отправить вас прямо к прослушиванию релиза!
            search_query = f"{artist} {title}".replace(" ", "+")
            bandcamp_link = f"https{C}{S}{S}bandcamp.com{S}search?q={search_query}"

            found_releases.append({
                "artist": artist.strip(),
                "title": title.strip(),
                "url": bandcamp_link
            })
            seen_titles.add(full_title)

    except Exception as e:
        print(f"Ошибка при работе со всемирным музыкальным индексом: {e}")
        
    print(f"Всего альбомов просканировано в глобальном индексе: {total_index_items}")
    print(f"Отобрано чистого блэк-металла: {len(found_releases)}")
    return found_releases[:15], total_index_items

def send_to_telegram(releases, total_items):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (GLOBAL MUSIC INDEX)</b>\n\n"
        msg += f"Глобальный музыкальный индекс открыт! Обработано релизов: <code>{total_items}</code>.\n"
        msg += "Но подходящего под критерии блэк-металла в базе пока не зафиксировано."
    else:
        msg = f"<b>🇳🇴 АНДЕГРАУНДНЫЙ БЛЭК-МЕТАЛ УЛОВ ({months_ru[now.month]} {now.year})</b>\n\n"
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
    results, raw_total = parse_via_music_index()
    send_to_telegram(results, raw_total)
    
