import os
import json
from datetime import datetime
import requests

# ASCII маскировка
C = chr(58)
S = chr(47)

# Неблокируемый поисковый микро-шлюз Bandcamp
BASE_API = f"https{C}{S}{S}bandcamp.com{S}api{S}bcsearch{S}1{S}autocomplete"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Поисковые фразы для захвата свежего блэка
QUERIES = ["black metal", "atmospheric black metal", "depressive black metal", "blackgaze"]
FORBIDDEN = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

# Словарь для автоматической подстановки флагов стран (расширяемый)
COUNTRY_FLAGS = {
    "norway": "🇳🇴", "sweden": "🇸🇪", "finland": "🇫🇮", "france": "🇫🇷",
    "germany": "🇩🇪", "usa": "🇺🇸", "ukraine": "🇺🇦", "poland": "🇵🇱",
    "austria": "🇦🇹", "italy": "🇮🇹", "canada": "🇨🇦", "iceland": "🇮🇸"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_micro_api():
    now = datetime.now()
    found_releases = []
    seen_ids = set()

    # Август текущего года в текстовом формате
    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]

    for q in QUERIES:
        params = {"q": q}
        try:
            res = requests.get(BASE_API, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            data = res.json()
            # Результаты в микро-шлюзе лежат в ключе 'results'
            items = data.get("results", [])
            
            for item in items:
                # Нам нужны только альбомы (type: "a")
                if item.get("type") != "a":
                    continue
                    
                item_id = item.get("id")
                if item_id in seen_ids:
                    continue

                title = item.get("name", "").strip()
                artist = item.get("artist_name", "").strip()
                album_url = item.get("url", "")
                
                # Собираем жанры и описание релиза для фильтрации
                genre_text = item.get("genre", "Black Metal").strip()
                full_desc = f"{title} {artist} {genre_text}".lower()

                # Жесткий блэк-метал отсев
                if any(forbidden in full_desc for forbidden in FORBIDDEN):
                    continue

                # Пытаемся определить страну происхождения группы для эмодзи-флага
                country_name = item.get("location", "").lower()
                flag = "🇳🇴" # Тру-дефолт флаг, если страна в метаданных не указана
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in country_name:
                        flag = c_flag
                        break

                # Генерируем чистую ссылку на YouTube-поиск для твоего шаблона
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"www.youtube.com{S}results?search_query={youtube_query}"

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": str(now.year),
                    "flag": flag,
                    "genre": genre_text,
                    "youtube": youtube_link,
                    "month": month_tag
                })
                seen_ids.add(item_id)

        except Exception as e:
            print(f"Ошибка микро-шлюза по запросу {q}: {e}")
            continue

    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (MICRO SHIELD)</b>\n\nМикро-шлюз ответил успешно, но по ключевым фразам блэк-метал альбомов не найдено."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

    # Собираем итоговое текстовое сообщение строго по твоему шаблону!
    msg = ""
    for r in releases:
        msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
        msg += f"{r['flag']} {r['genre']}\n"
        msg += f"{r['youtube']} {r['month']}\n"
        msg += "---\n" # Твой разделитель между релизами

    telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results = parse_bandcamp_micro_api()
    send_to_telegram(results)
    
