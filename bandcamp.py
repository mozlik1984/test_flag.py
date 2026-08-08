import os
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка путей
C = chr(58)
S = chr(47)

# Неблокируемый поисковый шлюз DuckDuckGo (HTML-версия без JS)
BASE_DDG = f"https{C}{S}{S}://duckduckgo.com{S}html{S}"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Поисковые фразы для выуживания свежего блэка из индекса
QUERIES = [
    'site:bandcamp.com "black metal" "album" "2026"',
    'site:bandcamp.com "atmospheric black metal" "2026"',
    'site:bandcamp.com "depressive black metal" "2026"'
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

def parse_bandcamp_via_search_index():
    now = datetime.now()
    found_releases = []
    seen_identities = set()

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for q_text in QUERIES:
        payload = {"q": q_text}
        try:
            # Стучимся в DuckDuckGo HTML — он полностью открыт для GitHub Actions
            res = requests.post(BASE_DDG, data=payload, headers=HEADERS, timeout=20)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # В HTML-версии поисковика все результаты лежат в блоках с классом result__body
            results = soup.find_all("div", class_="result__body")
            
            for item in results:
                title_tag = item.find("a", class_="result__url")
                snippet_tag = item.find("a", class_="result__snippet")
                
                if not title_tag:
                    continue
                    
                # Текст ссылки в поисковике обычно имеет формат: "Album Name | Band Name" или "Artist - Album"
                raw_title = title_tag.text.strip()
                snippet_text = snippet_tag.text.strip().lower() if snippet_tag else ""
                
                # Чистим заголовок от хвостов поисковых систем
                if " | " in raw_title:
                    parts = raw_title.split(" | ")
                    title = parts[0].strip()
                    artist = parts[1].replace("Bandcamp", "").strip()
                elif " - " in raw_title:
                    artist, title = raw_title.split(" - ", 1)
                    title = title.replace("Bandcamp", "").strip()
                else:
                    title = raw_title
                    artist = "Underground Artist"

                # Фильтрация (проверяем заголовок и поисковый сниппет на запрещенные слова)
                full_desc = f"{title} {artist} {snippet_text}".lower()
                if any(forbidden in full_desc for forbidden in FORBIDDEN_KEYWORDS):
                    continue
                    
                full_identity = f"{artist} - {title}".lower()
                if full_identity in seen_identities or "unknown" in full_identity:
                    continue

                # Пытаемся автоматически поставить флаг, если страна упомянута в описании альбома
                flag = "🇳🇴" # Тру-дефолт флаг по умолчанию
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in snippet_text or c_key in full_desc:
                        flag = c_flag
                        break

                # Формируем ссылку на YouTube по твоему шаблону
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                # Определяем сочный поджанр на основе текста сниппета
                genre_text = "Black Metal"
                if "atmospheric" in snippet_text:
                    genre_text = "Atmospheric Black Metal"
                elif "depressive" in snippet_text or "dsbm" in snippet_text:
                    genre_text = "Depressive Black Metal"
                elif "gaze" in snippet_text or "blackgaze" in snippet_text:
                    genre_text = "Blackgaze"

                found_releases.append({
                    "artist": artist.strip(),
                    "title": title.strip(),
                    "year": current_year,
                    "flag": flag,
                    "genre": genre_text,
                    "youtube": youtube_link,
                    "month": month_tag
                })
                seen_identities.add(full_identity)

        except Exception as e:
            print(f"Ошибка чтения индекса поисковика по запросу {q_text}: {e}")
            continue

    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (INDEX BYPASS)</b>\n\nПоисковый индекс просканирован успешно, но свежих блэк-метал релизов по критериям очистки не зафиксировано."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

    # Собираем текстовое сообщение строго по твоему шаблону!
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
    results = parse_bandcamp_via_search_index()
    send_to_telegram(results)
    
