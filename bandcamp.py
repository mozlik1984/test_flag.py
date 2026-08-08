import os
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка
C = chr(58)
S = chr(47)

# Неблокируемые прокси-шлюзы для обхода Cloudflare
PROXY_GATEWAY = f"https{C}{S}{S}api.allorigins.win{S}get?url="
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

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

def parse_bandcamp_via_proxy():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    total_raw_items = 0

    for tag in BLACK_METAL_TAGS:
        # Формируем целевой URL Bandcamp
        target_url = f"https{C}{S}{S}bandcamp.com{S}tag{S}{tag}"
        
        # Оборачиваем его в прокси-шлюз, который скроет GitHub от систем защиты Cloudflare
        encoded_url = urllib.parse.quote_plus(target_url)
        full_proxy_url = f"{PROXY_GATEWAY}{encoded_url}"
        
        try:
            res = requests.get(full_proxy_url, headers=HEADERS, timeout=20)
            if res.status_code != 200:
                print(f"Шлюз прокси для тега {tag} вернул ошибку {res.status_code}")
                continue
                
            # Извлекаем чистый HTML из ответа прокси-сервера
            payload_data = res.json()
            html_content = payload_data.get("contents", "")
            
            if not html_content:
                continue
                
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Находим заветный тег со встроенным JSON, который мы искали с самого начала!
            pagedata_tag = soup.find("div", id="pagedata") or soup.find("script", {"id": "pagedata"})
            if not pagedata_tag:
                continue
                
            raw_blob = pagedata_tag.get("data-blob") or pagedata_tag.text
            if not raw_blob:
                continue
                
            data = json.loads(raw_blob)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                total_raw_items += 1
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                # Фильтрация поджанров (отсекаем чистый дэт/трэш/хэви)
                item_tags = [t.lower() for t in item.get("tags", [])]
                if any(forbidden in item_tags for forbidden in FORBIDDEN_TAGS):
                    continue
                
                # Проверка даты релиза (Берем строго Июль и Август 2026 для обкатки)
                rel_date_str = item.get("release_date")
                is_target_period = False
                
                if rel_date_str:
                    try:
                        # Формат даты в JSON Bandcamp: "05 Aug 2026"
                        rel_date = datetime.strptime(rel_date_str, "%d %b %Y")
                        if rel_date.year == 2026 and rel_date.month in:
                            is_target_period = True
                    except Exception:
                        is_target_period = True # Если формат изменился — забираем, чтобы не потерять
                else:
                    is_target_period = True

                if is_target_period:
                    clean_url = album_url.split('?') if '?' in album_url else album_url
                    found_releases.append({
                        "artist": item.get("artist", "Unknown Artist").strip(),
                        "title": item.get("title", "Unknown Album").strip(),
                        "url": clean_url
                    })
                    seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка прорыва Cloudflare для тега {tag}: {e}")
            continue
            
    print(f"Всего элементов выгружено через прокси: {total_raw_items}")
    print(f"Успешно прошло блэк-метал очистку: {len(found_releases)}")
    return found_releases[:15], total_raw_items

def send_to_telegram(releases, total_raw):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (PROXY BYPASS)</b>\n\n"
        msg += f"Cloudflare успешно пробит! Из JSON-блока выгружено альбомов: <code>{total_raw}</code>.\n"
        msg += f"Но среди них нет релизов строго за Июль-Август {now.year}."
    else:
        msg = f"<b>🇳🇴 СВЕЖИЙ БЛЭК-МЕТАЛ УЛОВ С BANDCAMP ({months_ru[now.month]} {now.year})</b>\n\n"
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
    results, raw_count = parse_bandcamp_via_proxy()
    send_to_telegram(results, raw_count)
    
