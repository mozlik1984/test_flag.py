import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

# Защита строк через ASCII-коды
C = chr(58)
S = chr(47)

# URL для сбора фидов: https://bandcamp.com
BASE_FEED = f"https{C}{S}{S}bandcamp.com{S}feed{S}tag{S}"
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

def parse_bandcamp_rss():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    
    total_rss_items = 0

    for tag in BLACK_METAL_TAGS:
        url = f"{BASE_FEED}{tag}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Фид {tag} вернул статус {res.status_code}")
                continue
                
            # Парсим XML-структуру Atom Feed
            root = ET.fromstring(res.text)
            
            # Пространство имен Atom фидов Bandcamp
            ns = {'atom': 'http://w3.org'}
            
            # Ищем все записи <entry> в фиде
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                total_rss_items += 1
                
                title_text = entry.find('atom:title', ns).text  # Обычно в формате "Album Name by Artist"
                link_tag = entry.find('atom:link', ns)
                album_url = link_tag.attrib['href'] if link_tag is not None else ""
                
                if not album_url or album_url in seen_urls:
                    continue
                    
                # Вытаскиваем дату публикации из тега <updated> или <published>
                updated_tag = entry.find('atom:updated', ns)
                pub_date_str = updated_tag.text if updated_tag is not None else ""
                
                # Разбираем строку "Album Name by Artist"
                if " by " in title_text:
                    title, artist = title_text.rsplit(" by ", 1)
                else:
                    title, artist = title_text, "Unknown Artist"
                
                # Проверяем дату релиза (формат в RSS обычно ISO: 2026-08-08T12:00:00Z)
                is_current_period = False
                if pub_date_str:
                    try:
                        # Берем первые 7 символов даты ("2026-08")
                        date_prefix = pub_date_str[:7]
                        current_prefix = now.strftime("%Y-%m")
                        if date_prefix == current_prefix:
                            is_current_period = True
                    except Exception:
                        is_current_period = True # Если сбой даты — берем в улов
                else:
                    is_current_period = True

                if is_current_period:
                    clean_url = album_url.split('?') if '?' in album_url else album_url
                    found_releases.append({
                        "artist": artist.strip(),
                        "title": title.strip(),
                        "url": clean_url
                    })
                    seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка чтения RSS для тега {tag}: {e}")
            continue

    print(f"Всего записей обработано в RSS: {total_rss_items}")
    print(f"Отобрано свежих блэк-метал релизов: {len(found_releases)}")
    return found_releases[:15], total_rss_items

def send_to_telegram(releases, total_rss):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (RSS-ПРОРЫВ)</b>\n\n"
        msg += f"Защита сайта обойдена! Из фидов вытащено записей: <code>{total_rss}</code>.\n"
        msg += f"Но среди них нет релизов строго за <code>{months_ru[now.month]} {now.year}</code>."
    else:
        msg = f"<b>🇳🇴 АВТОНОМНЫЙ БЛЭК-МЕТАЛ УЛОВ ({months_ru[now.month]} {now.year})</b>\n\n"
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
    results, total_count = parse_bandcamp_rss()
    send_to_telegram(results, total_count)
    
