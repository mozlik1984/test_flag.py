import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Строгое архитектурное правило: сборка служебных знаков через ASCII
d = chr(46)
c = chr(58)
s = chr(47)

# Посимвольная сборка неблокируемого шлюза виджетов: https://bandcamp.com
EMBED_DOM = f"https{c}{s}{s}bandcamp{d}com{s}EmbeddedPlayer"

# Базовый адрес отправки сообщений Telegram: https://telegram.org
BASE_TG = f"https{c}{s}{s}api{d}telegram{d}org{s}bot"

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

def parse_bandcamp_embedded_perfect():
    now = datetime.now()
    found_releases = []
    seen_identities = set()
    
    # Карта отладки (ВСЕГДА отправляется в Telegram)
    debug_log = {
        "status_code": 0,
        "raw_text_length": 0,
        "total_parsed_items": 0,
        "skipped_by_filters": 0,
        "error_message": "",
        "sample_titles": []
    }

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for tag in BLACK_METAL_TAGS:
        # v=2 — это параметр, запрашивающий сетку со свежими релизами внутри плеера
        params = {"tag": tag, "v": "2"}
        try:
            res = requests.get(EMBED_DOM, params=params, headers=headers, timeout=15)
            
            if debug_log["status_code"] == 0:
                debug_log["status_code"] = res.status_code
                debug_log["raw_text_length"] = len(res.text)

            if res.status_code != 200 or not res.text:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Внутри верстки плеера альбомы всегда лежат в блоках art-link или visual
            artworks = soup.find_all("div", class_="visual") or soup.find_all("a", class_="art-link") or soup.find_all("img")
            
            for art in artworks:
                img_tag = art if art.name == "img" else art.find("img")
                if not img_tag or not img_tag.has_attr("alt"):
                    continue
                    
                # Названия зашиты в атрибут alt картинок в формате "Album Name by Band Name"
                album_info = img_tag["alt"].strip()
                if not album_info or " by " not in album_info:
                    continue
                    
                debug_log["total_parsed_items"] += 1
                
                if len(debug_log["sample_titles"]) 🔎 ПОСТОЯННЫЙ ЛОГ ОТЛАДКИ EMBEDDED PLAYER</b>\n\n"
    msg += f"<b>📊 Метрики шлюза:</b>\n"
    msg += f"• Код ответа Bandcamp: <code>{debug_log['status_code']}</code>\n"
    msg += f"• Получено символов HTML: <code>{debug_log['raw_text_length']}</code>\n"
    msg += f"• Элементов найдено в верстке: <code>{debug_log['total_parsed_items']}</code>\n"
    msg += f"• Отсеяно фильтром поджанров: <code>{debug_log['skipped_by_filters']}</code>\n"
    msg += f"• Что прислал плеер (сырые строки): <code>[{samples_str}]</code>\n"
    if debug_log["error_message"]:
        msg += f"• Ошибка внутри кода: <code>{debug_log['error_message']}</code>\n"
    msg += "\n"
    
    if not releases:
        msg += "❌ <b>Результат фильтра:</b> Живых блэк-метал новинок внутри виджета не распознано."
    else:
        msg += "🔥 <b>НОВЫЕ ЖИВЫЕ РЕЛИЗЫ С BANDCAMP:</b>\n\n"
        for r in releases:
            msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
            msg += f"{r['flag']} {r['genre']}\n"
            msg += f"https{c}{s}{s}youtube{d}com {r['month']}\n"  # Твой жесткий формат ссылки-заглушки!
            msg += "---\n"

    # Безопасная склейка адреса отправки Telegram
    telegram_url = f"{BASE_TG}{BOT_TOKEN}{s}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    results, log_data = parse_bandcamp_embedded_perfect()
    send_to_telegram(results, log_data)
    
