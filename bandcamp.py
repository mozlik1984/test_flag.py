import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Строгое архитектурное правило: сборка служебных знаков и эмодзи через ASCII/Юникод
d = chr(46)
c = chr(58)
s = chr(47)

# Собираем эмодзи через Юникод-коды, чтобы телефон не ломал синтаксис!
EMOJI_LUPA = chr(0x1F50E)  # 🔎
EMOJI_DIAG = chr(0x1F4CA)  # 📊
EMOJI_CROSS = chr(0x274C)  # ❌
EMOJI_FIRE = chr(0x1F525)   # 🔥
EMOJI_DEFAULT_FLAG = chr(0x1F1E7) + chr(0x1F1FB)  # 🇧🇻 (Тру-дефолт флаг острова Буве для блэка)

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

# Кодируем флаги стран через пары Юникод-символов региональных индикаторов
COUNTRY_FLAGS = {
    "norway": chr(0x1F1E6) + chr(0x1F1F4),        # 🇳🇴
    "sweden": chr(0x1F1F8) + chr(0x1F1EA),        # 🇸🇪
    "finland": chr(0x1F1EB) + chr(0x1F1EE),       # 🇫🇮
    "france": chr(0x1F1EB) + chr(0x1F1F7),        # 🇫🇷
    "germany": chr(0x1F1DE) + chr(0x1F1EA),       # 🇩🇪
    "usa": chr(0x1F1FA) + chr(0x1F1F8),           # 🇺🇸
    "united states": chr(0x1F1FA) + chr(0x1F1F8), # 🇺🇸
    "ukraine": chr(0x1F1FA) + chr(0x1F1E6),       # 🇺🇦
    "poland": chr(0x1F1F5) + chr(0x1F1B1),        # 🇵🇱
    "austria": chr(0x1F1E6) + chr(0x1F1F9),       # 🇦🇹
    "italy": chr(0x1F1EE) + chr(0x1F1F9),         # 🇮🇹
    "canada": chr(0x1F1E4) + chr(0x1F1E6),        # 🇨🇦
    "iceland": "🇮🇸", "greece": "🇬🇷", "russia": "🇷🇺", "united kingdom": "🇬🇧"
}

def parse_bandcamp_embedded_perfect():
    now = datetime.now()
    found_releases = []
    seen_identities = set()
    
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
        params = {"tag": tag, "v": "2"}
        try:
            res = requests.get(EMBED_DOM, params=params, headers=headers, timeout=15)
            
            if debug_log["status_code"] == 0:
                debug_log["status_code"] = res.status_code
                debug_log["raw_text_length"] = len(res.text)

            if res.status_code != 200 or not res.text:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            artworks = soup.find_all("div", class_="visual") or soup.find_all("a", class_="art-link") or soup.find_all("img")
            
            for art in artworks:
                img_tag = art if art.name == "img" else art.find("img")
                if not img_tag or not img_tag.has_attr("alt"):
                    continue
                    
                album_info = img_tag["alt"].strip()
                if not album_info or " by " not in album_info:
                    continue
                    
                debug_log["total_parsed_items"] += 1
                
                if len(debug_log["sample_titles"]) {EMOJI_LUPA} ПОСТОЯННЫЙ ЛОГ ОТЛАДКИ EMBEDDED PLAYER</b>\n\n"
    msg += f"<b>{EMOJI_DIAG} Метрики шлюза:</b>\n"
    msg += f"• Код ответа Bandcamp: <code>{debug_log['status_code']}</code>\n"
    msg += f"• Получено символов HTML: <code>{debug_log['raw_text_length']}</code>\n"
    msg += f"• Элементов найдено в верстке: <code>{debug_log['total_parsed_items']}</code>\n"
    msg += f"• Отсеяно фильтром поджанров: <code>{debug_log['skipped_by_filters']}</code>\n"
    msg += f"• Что прислал плеер (сырые строки): <code>[{samples_str}]</code>\n"
    if debug_log["error_message"]:
        msg += f"• Ошибка внутри кода: <code>{debug_log['error_message']}</code>\n"
    msg += "\n"
    
    if not releases:
        msg += f"{EMOJI_CROSS} <b>Результат фильтра:</b> Живых блэк-метал новинок внутри виджета не распознано."
    else:
        msg += f"{EMOJI_FIRE} <b>НОВЫЕ ЖИВЫЕ РЕЛИЗЫ С BANDCAMP:</b>\n\n"
        for r in releases:
            msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
            msg += f"{r['flag']} {r['genre']}\n"
            msg += f"https{c}{s}{s}youtube{d}com {r['month']}\n"
            msg += "---\n"

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
    
