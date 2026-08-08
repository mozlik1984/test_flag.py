import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Жесткая сборка доменов через ASCII для защиты от искажения строк при копировании
# C = ':', S = '/'
C = chr(58)
S = chr(47)

# Собираем базовый URL: https://bandcamp.com
BASE_BC = f"https{C}{S}{S}bandcamp.com{S}tag{S}"

# Собираем URL Telegram API: https://telegram.org
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

# Конфигурация
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_TAGS = ["thrash-metal", "death-metal", "heavy-metal", "power-metal", "metalcore"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_current_month():
    now = datetime.now()
    found_releases = []
    seen_urls = set()

    for tag in BLACK_METAL_TAGS:
        # Склейка через ASCII-переменную гарантирует правильный URL без дефектов
        url = f"{BASE_BC}{tag}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Пропуск тега {tag}: статус {res.status_code}")
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            pagedata_tag = soup.find("div", id="pagedata") or soup.find("script", {"id": "pagedata"})
            if not pagedata_tag:
                continue
                
            data = json.loads(pagedata_tag.get("data-blob") or pagedata_tag.text)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                item_tags = [t.lower() for t in item.get("tags", [])]
                if any(forbidden in item_tags for forbidden in FORBIDDEN_TAGS):
                    continue
                
                # Безопасно очищаем реферальную ссылку
                clean_url = album_url.split('?')[0] if '?' in album_url else album_url
                
                rel_date_str = item.get("release_date")
                if rel_date_str:
                    try:
                        rel_date = datetime.strptime(rel_date_str, "%d %b %Y")
                        if rel_date.month == now.month and rel_date.year == now.year:
                            found_releases.append({
                                "artist": item.get("artist"),
                                "title": item.get("title"),
                                "url": clean_url
                            })
                            seen_urls.add(album_url)
                    except Exception:
                        found_releases.append({
                            "artist": item.get("artist"),
                            "title": item.get("title"),
                            "url": clean_url
                        })
                        seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка при обработке тега {tag}: {e}")
            continue
            
    print(f"Всего найдено подходящих релизов: {len(found_releases)}")
    return found_releases[:15]

def send_to_telegram(releases):
    if not releases:
        msg = "<b>🇳🇴 АВТОНОМНЫЙ БЛЭК-МЕТАЛ ПАРСЕР</b>\n\nЗа текущий период новых релизов на главной странице не обнаружено."
    else:
        months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
        now = datetime.now()
        msg = f"<b>🇳🇴 АВТОНОМНЫЙ БЛЭК-МЕТАЛ УЛОВ ({months_ru[now.month]} {now.year})</b>\n\n"
        for r in releases:
            msg += f"• <code>{r['artist']} - {r['title']}</code>\n🔗 {r['url']}\n\n"

    if not BOT_TOKEN:
        print("Ошибка: Токен Telegram (TELEGRAM_TOKEN) не найден в Secrets!")
        return

    # Безопасная склейка эндпоинта Telegram
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
        print(f"Ошибка отправки в Telegram API: {res.status_code} - {res.text}")

if __name__ == "__main__":
    results = parse_bandcamp_current_month()
    send_to_telegram(results)
    
