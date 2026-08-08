import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

C = chr(58)
S = chr(47)

BASE_BC = f"https{C}{S}{S}bandcamp.com{S}tag{S}"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def parse_bandcamp_html():
    found_releases = []
    seen_urls = set()
    
    total_parsed_html_items = 0

    for tag in BLACK_METAL_TAGS:
        url = f"{BASE_BC}{tag}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Находим карточки альбомов прямо в HTML-верстке страницы
            items = soup.find_all("li", class_="item") or soup.find_all("div", class_="item")
            if not items:
                # Альтернативный поиск по сетке dig deeper
                items = soup.select(".dig-deeper-results .item") or soup.select(".item")

            for item in items:
                total_parsed_html_items += 1
                
                # Извлекаем ссылку на альбом
                link_tag = item.find("a", href=True)
                if not link_tag:
                    continue
                album_url = link_tag["href"]
                
                # Если ссылка относительная — дописываем базовый домен
                if album_url.startswith("/"):
                    album_url = f"https{C}{S}{S}bandcamp.com{album_url}"
                    
                if album_url in seen_urls:
                    continue

                # Извлекаем название альбома и группу
                title_tag = item.find(class_="title") or item.find(class_="album")
                artist_tag = item.find(class_="artist") or item.find(class_="band")
                
                # Извлекаем обложку альбома
                img_tag = item.find("img", src=True)
                image_url = ""
                if img_tag:
                    image_url = img_tag.get("data-original") or img_tag["src"]

                title = title_tag.text.strip() if title_tag else "Unknown Album"
                artist = artist_tag.text.strip() if artist_tag else "Unknown Artist"
                
                # Очищаем ссылку от мусора
                clean_url = album_url.split('?')[0] if '?' in album_url else album_url

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "url": clean_url,
                    "image": image_url
                })
                seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка парсинга HTML для тега {tag}: {e}")
            continue
            
    print(f"Парсер зафиксировал элементов в верстке: {total_parsed_html_items}")
    print(f"Успешно извлечено чистых релизов: {len(found_releases)}")
    return found_releases[:10], total_parsed_html_items

def send_to_telegram(releases, total_raw):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    if not releases:
        msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ ПАРСЕР (ВЕРСТКА)</b>\n\n"
        msg += f"Сканирование завершено. В HTML коде найдено блоков: <code>{total_raw}</code>.\n"
        msg += "Но карточки релизов вытащить не удалось. Защита Bandcamp."
        
        telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
        payload = {"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(telegram_url, json=payload)
        return

    # Если релизы найдены — отправляем их красивым списком
    msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ УЛОВ ({months_ru[now.month]} {now.year})</b>\n\n"
    for r in releases:
        msg += f"• <code>{r['artist']} - {r['title']}</code>\n🔗 {r['url']}\n\n"

    telegram_url = f"{BASE_TG}{BOT_TOKEN}{S}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False  # Разрешаем Телеграму подтянуть превью первой ссылки
    }
    
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results, raw_count = parse_bandcamp_html()
    send_to_telegram(results, raw_count)
    
