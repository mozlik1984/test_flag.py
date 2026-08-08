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

# ВРЕМЕННО: Оставляем только один самый гигантский тег для теста пробива
TEST_TAGS = ["metal"]

# ВРЕМЕННО ОТКЛЮЧЕНО: Пропускаем абсолютно любые жанры ради теста!
FORBIDDEN_KEYWORDS = []

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

    for tag in TEST_TAGS:
        url = f"{BASE_BC}{tag}"
        try:
            # Стучимся напрямую на Bandcamp сквозь Cloudflare
            res = scraper.get(url, timeout=25)
            if res.status_code != 200:
                print(f"Защита не пробита для тега {tag}: статус {res.status_code}")
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            pagedata_tag = soup.find("div", id="pagedata") or soup.find("script", {"id": "pagedata"})
            if not pagedata_tag:
                print("КРИТИЧЕСКИЙ СБОЙ: Тег pagedata не найден на странице!")
                continue
                
            raw_blob = pagedata_tag.get("data-blob") or pagedata_tag.text
            if not raw_blob:
                print("КРИТИЧЕСКИЙ СБОЙ: data-blob оказался пустым!")
                continue
                
            data = json.loads(raw_blob)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            print(f"Парсер извлек сырых элементов из тега {tag}: {len(dig_deeper)}")
            
            for item in dig_deeper:
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                title = item.get("title", "Unknown Album").strip()
                artist = item.get("artist", "Unknown Artist").strip()
                
                # Собираем жанровое описание
                genre_text = item.get("genre") or tag.replace("-", " ").title()
                
                # Временный тестовый прогон: берем всё без фильтрации!
                location = item.get("artist_location", "").lower()
                flag = "🏴‍☠️"  # Тестовый пиратский флаг, если локация не определена
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
            
    print(f"Успешно прошло тестовую выгрузку: {len(found_releases)}")
    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>⚠️ ТЕСТОВЫЙ ПАРСЕР (ЖАНР METAL)</b>\n\nДаже по общему тегу 'metal' пустая выдача. Защита Cloudflare полностью заблокировала структуру pagedata."
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
    
    res = requests.post(telegram_url, json=payload)
    if res.status_code == 200:
        print("Результат успешно отправлен в Telegram!")
    else:
        print(f"Ошибка отправки в TG: {res.status_code} - {res.text}")

if __name__ == "__main__":
    results = parse_bandcamp_hardcore()
    send_to_telegram(results)
    
