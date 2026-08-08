import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as cloud_requests

# Жесткое правило: сборка служебных знаков через ASCII
d = chr(46)
c = chr(58)
s = chr(47)

# Официальный внутренний поисковый шлюз Bandcamp
BASE_API = f"https{c}{s}{s}bandcamp{d}com{s}api{s}v1{s}search"
BASE_TG = f"https{c}{s}{s}api{d}telegram{d}org{s}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

QUERIES = ["black metal album", "atmospheric black metal", "depressive black metal"]
FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

def run_furious_parser():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    
    # Счётчики для лога отладки
    status_code = 0
    total_search_items = 0
    skipped_by_filters = 0
    sample_titles = []

    month_tag = now.strftime("%b").upper()
    current_year = str(now.year)

    for query in QUERIES:
        params = {"q": query, "item_type": "a", "page": 1}
        try:
            # Обходим Cloudflare, маскируясь под мобильный движок Chrome
            res = cloud_requests.get(BASE_API, params=params, impersonate="chrome110", timeout=15)
            
            if status_code == 0:
                status_code = res.status_code
                
            if res.status_code != 200:
                continue
                
            data = res.json()
            items = data.get("results", [])
            
            for item in items:
                total_search_items += 1
                album_url = item.get("item_url") or item.get("url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                title = item.get("name", "Unknown Album").strip()
                artist = item.get("artist_name", "Unknown Artist").strip()
                
                # Собираем теги релиза для блэк-метал очистки
                tags_list = [t.lower() for t in item.get("tags", [])]
                full_desc = f"{title} {artist} {' '.join(tags_list)}".lower()
                
                if any(forbidden in full_desc for forbidden in FORBIDDEN_KEYWORDS):
                    skipped_by_filters += 1
                    continue

                if len(sample_titles) < 3:
                    sample_titles.append(f"{artist} - {title}"[:35])

                # Парсим локацию группы для текстовой разметки страны
                location = item.get("location", "Norway").strip()
                if ", " in location:
                    location = location.split(", ")[-1]

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": current_year,
                    "country": location,
                    "genre": "Black Metal"
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Error inside loop: {e}")
            continue

    # Сборка финального сообщения строго по твоему текстовому шаблону
    samples_str = ", ".join([f"'{t}'" for t in sample_titles])
    
    msg = "DIAGNOSTIC LOG SEARCH API\n\n"
    msg += "METRICS:\n"
    msg += f"Bandcamp status: {status_code}\n"
    msg += f"Total search items: {total_search_items}\n"
    msg += f"Skipped by filters: {skipped_by_filters}\n"
    msg += f"Raw items snippet: [{samples_str}]\n\n"
    
    if not found_releases:
        msg += "RESULT: No pure black metal releases found in search index."
    else:
        msg += "NEW RELEASES FROM BANDCAMP:\n\n"
        for r in found_releases:
            msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
            msg += f"[{r['country']}] {r['genre']}\n"
            msg += f"https{c}{s}{s}youtube{d}com {month_tag}\n" # Идеально жесткая ссылка-заглушка!
            msg += "---\n"

    # Отправка отчета в Телеграм
    telegram_url = f"{BASE_TG}{BOT_TOKEN}{s}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    run_furious_parser()
  
