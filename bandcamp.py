import os
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка
C = chr(58)
S = chr(47)

# Каскад из трех независимых публичных прокси-серверов
PROXY_POOL = [
    f"https{C}{S}{S}api.allorigins.win{S}get?url=",
    f"https{C}{S}{S}://codetabs.com{S}cors-proxy{S}",
    f"https{C}{S}{S}corsproxy.io{S}?"
]

BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_TAGS = ["thrash-metal", "death-metal", "heavy-metal", "power-metal", "metalcore", "punk", "electronic"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_html_via_cascade(target_url):
    """Пытается скачать HTML через пулл прокси-серверов по очереди"""
    for proxy_base in PROXY_POOL:
        try:
            # Разные прокси требуют разного кодирования ссылки
            if "allorigins" in proxy_base:
                encoded_url = urllib.parse.quote_plus(target_url)
                full_url = f"{proxy_base}{encoded_url}"
            else:
                full_url = f"{proxy_base}{target_url}"
                
            res = requests.get(full_url, headers=HEADERS, timeout=20)
            if res.status_code == 200:
                # У allorigins HTML-код зашит внутрь JSON ключа 'contents'
                if "allorigins" in proxy_base:
                    return res.json().get("contents", "")
                return res.text
        except Exception as e:
            print(f"Шлюз {proxy_base[:30]} не справился, пробуем следующий... Ошибка: {e}")
            continue
    return ""

def parse_bandcamp_via_proxy():
    found_releases = []
    seen_urls = set()
    total_raw_items = 0

    for tag in BLACK_METAL_TAGS:
        target_url = f"https{C}{S}{S}bandcamp.com{S}tag{S}{tag}"
        
        # Получаем HTML через систему каскадных прокси
        html_content = fetch_html_via_cascade(target_url)
        if not html_content:
            print(f"Ни один прокси не смог загрузить тег {tag}")
            continue
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
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
                    
                item_tags = [t.lower() for t in item.get("tags", [])]
                if any(forbidden in item_tags for forbidden in FORBIDDEN_TAGS):
                    continue
                
                clean_url = album_url.split('?') if '?' in album_url else album_url
                
                found_releases.append({
                    "artist": item.get("artist", "Unknown Artist").strip(),
                    "title": item.get("title", "Unknown Album").strip(),
                    "url": clean_url
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка обработки контента для тега {tag}: {e}")
            continue
            
    print(f"Всего элементов выгружено через прокси: {total_raw_items}")
    print(f"Успешно прошло блэк-метал очистку: {len(found_releases)}")
    return found_releases[:15], total_raw_items

def send_to_telegram(releases, total_raw):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (CASCADE PROXY)</b>\n\n"
        msg += f"Каскад прокси отработал. Из JSON-блока выгружено альбомов: <code>{total_raw}</code>.\n"
        msg += "Но ни один релиз не прошел жанровый фильтр-очистку от трэша/дэта."
    else:
        msg = f"<b>🇳🇴 ЕЖЕНЕДЕЛЬНЫЙ БЛЭК-МЕТАЛ УЛОВ С BANDCAMP ({months_ru[now.month]} {now.year})</b>\n\n"
        for r in releases:
            # Предохранитель на случай если url пришел в виде списка строк
            final_url = r['url'][0] if isinstance(r['url'], list) else r['url']
            msg += f"• <code>{r['artist']} - {r['title']}</code>\n🔗 {final_url}\n\n"

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
    
