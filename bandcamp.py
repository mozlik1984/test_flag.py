import os
import json
from datetime import datetime
import requests

# ASCII маскировка
C = chr(58)
S = chr(47)

# Стучимся в открытое API Веб-Архива, чтобы взять самый свежий снимок Bandcamp
BASE_WAYBACK = f"https{C}{S}{S}archive.org{S}wayback{S}available"
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

def parse_via_web_archive():
    found_releases = []
    seen_urls = set()
    total_snapshots = 0
    total_items_parsed = 0

    for tag in BLACK_METAL_TAGS:
        target_url = f"https{C}{S}{S}bandcamp.com{S}tag{S}{tag}"
        
        try:
            # 1. Спрашиваем у Веб-Архива ссылку на самый свежий снимок этой страницы
            avail_res = requests.get(BASE_WAYBACK, params={"url": target_url}, headers=HEADERS, timeout=15)
            if avail_res.status_code != 200:
                continue
                
            avail_data = avail_res.json()
            closest = avail_data.get("archived_snapshots", {}).get("closest", {})
            snapshot_url = closest.get("url")
            
            if not snapshot_url:
                print(f"Снимок для тега {tag} не найден в Веб-Архиве")
                continue
                
            total_snapshots += 1
            
            # 2. Скачиваем чистый HTML-код снимка (там внутри лежит тот самый pagedata JSON!)
            # Модифицируем ссылку (id_), чтобы получить чистый исходник без панели Архива
            if "web.archive.org/web/" in snapshot_url:
                snapshot_url = snapshot_url.replace("web.archive.org/web/", "web.archive.org/web/id_/")

            html_res = requests.get(snapshot_url, headers=HEADERS, timeout=20)
            if html_res.status_code != 200:
                continue
                
            html = html_res.text
            
            # 3. Выковыриваем JSON из верстки снимка вручную
            start_marker = 'data-blob="'
            if start_marker not in html:
                start_marker = 'id="pagedata" data-blob="'
                if start_marker not in html:
                    continue
                    
            start_idx = html.find(start_marker) + len(start_marker)
            end_idx = html.find('"', start_idx)
            
            raw_json = html[start_idx:end_idx]
            # Декодируем HTML сущности кавычек
            raw_json = raw_json.replace('&quot;', '"').replace('&amp;', '&')
            
            data = json.loads(raw_json)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                total_items_parsed += 1
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
            print(f"Ошибка парсинга Архива для тега {tag}: {e}")
            continue

    print(f"Успешно обработано снимков: {total_snapshots}")
    print(f"Всего извлечено альбомов из Архива: {total_items_parsed}")
    return found_releases[:15], total_items_parsed

def send_to_telegram(releases, total_parsed):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (WAYBACK CACHE)</b>\n\n"
        msg += f"Архив взломан! Из кэша вытащено элементов: <code>{total_parsed}</code>.\n"
        msg += "Но ни один из них не прошел финальную очистку жанров."
    else:
        msg = f"<b>🇳🇴 АНДЕГРАУНДНЫЙ БЛЭК-МЕТАЛ УЛОВ (ИЗ ВЕБ-АРХИВА)</b>\n\n"
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
    results, raw_total = parse_via_web_archive()
    send_to_telegram(results, raw_total)
    
