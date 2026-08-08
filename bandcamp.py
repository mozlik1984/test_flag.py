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

# Ключевые слова для поиска
QUERIES = ["black metal", "atmospheric black metal", "depressive black metal"]

# Словарь для флагов стран на основе локации группы
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
    seen_urls = set()

    # Формируем метку месяца для третьей строки (например, "AUG")
    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]

    for q in QUERIES:
        params = {"q": q}
        try:
            res = requests.get(BASE_API, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            data = res.json()
            items = data.get("results", [])
            
            for item in items:
                # Извлекаем ссылку на альбом/группу
                album_url = item.get("url", "")
                if not album_url or album_url in seen_urls:
                    continue
                    
                # Получаем имя артиста и название релиза
                # Поле 'name' в автодополнении часто содержит название релиза, а 'artist_name' - группу
                title = item.get("name", "Unknown Release").strip()
                artist = item.get("artist_name", "").strip()
                
                # Если имя артиста пустое (например, это карточка самой группы), 
                # переносим название в артисты, чтобы не ломать структуру
                if not artist:
                    artist = title
                    title = "Release"

                # Определяем жанровое описание. Если Bandcamp не отдал жанр, ставим Atmospheric Black Metal
                genre_text = item.get("genre") or item.get("stat") or "Atmospheric Black Metal"
                
                # Подбираем эмодзи-флаг страны по локации
                location = item.get("location", "").lower()
                flag = "🇳🇴"  # Тру-дефолт для блэка
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in location:
                        flag = c_flag
                        break

                # Формируем ссылку на YouTube-поиск для третьей строки вашего шаблона
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": str(now.year),
                    "flag": flag,
                    "genre": genre_text,
                    "youtube": youtube_link,
                    "month": month_tag
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка микро-шлюза: {e}")
            continue

    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (MICRO SHIELD)</b>\n\nДаже базовые результаты автодополнения пришли пустыми. Профилактика на сервере."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

    # Собираем итоговое текстовое сообщение строго по твоему шаблону!
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
    results = parse_bandcamp_micro_api()
    send_to_telegram(results)
    
