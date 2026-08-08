import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка путей
C = chr(58)
S = chr(47)

BASE_PLAYER = f"https{C}{S}{S}bandcamp.com{S}EmbeddedPlayer"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Для теста берем один главный тег, чтобы лог диагностики не раздувался
BLACK_METAL_TAGS = ["black-metal"]
FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_with_permanent_debug():
    now = datetime.now()
    found_releases = []
    
    # Карта отладки, которая ВСЕГДА будет отправляться в Telegram
    debug_log = {
        "status_code": 0,
        "html_length": 0,
        "found_divs_count": 0,
        "found_imgs_count": 0,
        "detected_classes_sample": [],
        "raw_html_snippet": "",
        "error_message": ""
    }

    url = f"{BASE_PLAYER}"
    params = {"tag": "black-metal", "v": "2"}
    
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=15)
        debug_log["status_code"] = res.status_code
        debug_log["html_length"] = len(res.text)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Считаем все базовые элементы на странице для диагностики
            all_divs = soup.find_all("div")
            all_imgs = soup.find_all("img")
            
            debug_log["found_divs_count"] = len(all_divs)
            debug_log["found_imgs_count"] = len(all_imgs)
            
            # Собираем примеры классов, которые вообще есть в верстке
            classes = set()
            for div in all_divs[:20]:
                if div.has_attr("class"):
                    classes.update(div["class"])
            debug_log["detected_classes_sample"] = list(classes)[:5]
            
            # Берем кусок верстки из середины страницы, где должна быть музыка
            debug_log["raw_html_snippet"] = res.text[2000:2700].replace("<", "&lt;").replace(">", "&gt;")
            
            # Наш текущий поисковый алгоритм
            artworks = soup.find_all("div", class_="visual") or soup.find_all("a", class_="art-link") or soup.find_all("li")
            
            for art in artworks[:10]:
                img_tag = art.find("img") if art.name != "img" else art
                if img_tag and img_tag.has_attr("alt"):
                    album_info = img_tag["alt"].strip()
                    if " by " in album_info:
                        title, artist = album_info.split(" by ", 1)
                        
                        if not any(forbidden in album_info.lower() for forbidden in FORBIDDEN_KEYWORDS):
                            youtube_query = f"{artist} {title}".replace(" ", "+")
                            found_releases.append({
                                "artist": artist.strip(),
                                "title": title.strip(),
                                "year": str(now.year),
                                "flag": "🇳🇴",
                                "genre": "Black Metal",
                                "youtube": f"://youtube.com{S}results?search_query={youtube_query}",
                                "month": "AUG"
                            })

    except Exception as e:
        debug_log["error_message"] = str(e)
        
    return found_releases, debug_log

def send_to_telegram(releases, debug_log):
    # Собираем диагностическую карту
    classes_str = ", ".join([f"'{c}'" for c in debug_log["detected_classes_sample"]])
    
    msg = f"<b>🔎 ПОСТОЯННЫЙ ЛОГ ОТЛАДКИ EMBEDDED</b>\n\n"
    msg += f"<b>📊 Метрики верстки:</b>\n"
    msg += f"• Код ответа Bandcamp: <code>{debug_log['status_code']}</code>\n"
    msg += f"• Вес HTML (символов): <code>{debug_log['html_length']}</code>\n"
    msg += f"• Всего тегов &lt;div&gt; на странице: <code>{debug_log['found_divs_count']}</code>\n"
    msg += f"• Всего тегов &lt;img&gt; на странице: <code>{debug_log['found_imgs_count']}</code>\n"
    msg += f"• Примеры классов на сайте: <code>[{classes_str}]</code>\n"
    if debug_log["error_message"]:
        msg += f"• Критическая ошибка кода: <code>{debug_log['error_message']}</code>\n"
    msg += "\n"
    
    msg += f"<b>Срез исходного HTML кода:</b>\n<code>{debug_log['raw_html_snippet']}</code>\n\n"
    
    if not releases:
        msg += "❌ <b>Результат фильтра:</b> Релизы не распознаны по старым классам."
    else:
        msg += "🔥 <b>Найденные релизы (Тест):</b>\n\n"
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
    results, log_data = parse_bandcamp_with_permanent_debug()
    send_to_telegram(results, log_data)
    
