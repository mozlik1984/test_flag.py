import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

# ASCII маскировка
C = chr(58)
S = chr(47)

# Используем Google News API как бесплатный и неубиваемый прокси-поисковик
BASE_GOOGLE = f"https{C}{S}{S}://google.com{S}rss{S}search"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Ключевые фразы для точечного поиска в индексе Google
BLACK_METAL_QUERIES = [
    'site:bandcamp.com "black metal" "album"',
    'site:bandcamp.com "atmospheric black metal"',
    'site:bandcamp.com "depressive black metal"'
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_via_google():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    total_google_items = 0

    # Определяем текстовый маркер текущего месяца для проверки (например, "Aug 2026")
    months_en = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
    current_month_str = months_en[now.month]
    current_year_str = str(now.year)

    for query in BLACK_METAL_QUERIES:
        # Формируем поисковый запрос для Google
        params = {'q': query, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}
        try:
            res = requests.get(BASE_GOOGLE, params=params, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            root = ET.fromstring(res.text)
            items = root.findall('.//item')
            
            for item in items:
                total_google_items += 1
                title_text = item.find('title').text # Формат обычно: "Album Name | Bandcamp"
                google_link = item.find('link').text
                
                # Чистим название от хвостов поисковика
                if " | " in title_text:
                    title_text = title_text.split(" | ")[0]
                elif " - " in title_text:
                    title_text = title_text.rsplit(" - ", 1)[0]

                # Проверяем на запрещенные поджанры
                if any(forbidden in title_text.lower() for forbidden in FORBIDDEN_KEYWORDS):
                    continue

                # Извлекаем дату публикации из поискового сниппета
                pub_date_str = item.find('pubDate').text # Родной формат: "Sat, 08 Aug 2026 12:00:00 GMT"
                
                is_valid_date = False
                if pub_date_str:
                    # Проверяем, что релиз относится к Июлю или Августу 2026 года
                    if current_year_str in pub_date_str and (current_month_str in pub_date_str or "Jul" in pub_date_str):
                        is_valid_date = True
                else:
                    is_valid_date = True

                if is_valid_date and google_link not in seen_urls:
                    found_releases.append({
                        "title": title_text.strip(),
                        "url": google_link
                    })
                    seen_urls.add(google_link)

        except Exception as e:
            print(f"Ошибка поиска Google по запросу {query}: {e}")
            continue

    print(f"Всего проиндексировано страниц в Google: {total_google_items}")
    print(f"Отобрано чистых блэк-релизов: {len(found_releases)}")
    return found_releases[:15], total_google_items

def send_to_telegram(releases, total_google):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (GOOGLE INDEX)</b>\n\n"
        msg += f"Поисковый индекс исследован. Найдено страниц Bandcamp: <code>{total_google}</code>.\n"
        msg += f"Но новых блэк-метал релизов строго за Июль-Август {now.year} в кэше поисковика пока нет."
    else:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ УЛОВ ИЗ КЭША GOOGLE ({months_ru[now.month]} {now.year})</b>\n\n"
        for r in releases:
            msg += f"• <code>{r['title']}</code>\n🔗 {r['url']}\n\n"

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
    results, raw_total = parse_bandcamp_via_google()
    send_to_telegram(results, raw_total)
    
