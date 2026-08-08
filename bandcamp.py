import os
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Настройка Selenium браузера
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

C = chr(58)
S = chr(47)
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

def parse_via_real_browser():
    now = datetime.now()
    found_releases = []
    seen_urls = set()

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    # Опции маскировки фонового браузера Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Запуск без экрана
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # Инициализируем Chrome драйвер внутри Linux-контейнера GitHub
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Ошибка запуска браузера Chrome: {e}")
        return []

    for tag in BLACK_METAL_TAGS:
        url = f"https{C}{S}{S}bandcamp.com{S}tag{S}{tag}"
        try:
            driver.get(url)
            time.sleep(6) # Ждем 6 секунд, пока Cloudflare прогрузит скрипты защиты
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
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
                
                item_tags = [t.lower() for t in item.get("tags", [])]
                genre_text = item.get("genre") or tag.replace("-", " ").title()
                
                full_desc_lower = f"{title} {artist} {' '.join(item_tags)}".lower()
                if any(forbidden in full_desc_lower for forbidden in FORBIDDEN_KEYWORDS):
                    continue
                
                location = item.get("artist_location", "").lower()
                flag = "🇳🇴"
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in location:
                        flag = c_flag
                        break

                # Прямая ссылка на YouTube без ASCII костылей — теперь она будет монолитной!
                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"https://youtube.com{youtube_query}"

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
            print(f"Ошибка обработки тега {tag}: {e}")
            continue
            
    driver.quit()
    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (SELENIUM BROWSER)</b>\n\nДаже через реальный браузер выдача пуста. Страница тегов обновила структуру pagedata."
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        requests.post(telegram_url, json={"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        return

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
    results = parse_via_real_browser()
    send_to_telegram(results)
    
