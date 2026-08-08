import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as cloud_requests

# Архитектурное правило сборки доменов через ASCII
d = chr(46)
c = chr(58)
s = chr(47)

# Неблокируемый шлюз виджетов: https://bandcamp.com
EMBED_DOM = f"https{c}{s}{s}bandcamp{d}com{s}EmbeddedPlayer"
BASE_TG = f"https{c}{s}{s}api{d}telegram{d}org{s}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

def run_parser():
    now = datetime.now()
    found_releases = []
    seen_identities = set()
    
    # Карта отладки
    status_code = 0
    html_length = 0
    total_parsed_items = 0
    skipped_by_filters = 0
    sample_titles = []

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    # Имитируем реальный браузер Chrome через curl_cffi
    for tag in BLACK_METAL_TAGS:
        params = {"tag": tag, "v": "2"}
        try:
            res = cloud_requests.get(EMBED_DOM, params=params, impersonate="chrome110", timeout=15)
            
            if status_code == 0:
                status_code = res.status_code
                html_length = len(res.text)

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
                    
                total_parsed_items += 1
                if len(sample_titles) {r['artist']} - {r['title']} ({r['year']})</code>\n"
            msg += f"Genre: {r['genre']}\n"
            msg += f"https{c}{s}{s}youtube{d}com {r['month']}\n"
            msg += "---\n"

    # Отправка через стандартный requests (Телеграм нас не блочит)
    telegram_url = f"{BASE_TG}{BOT_TOKEN}{s}sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    run_parser()
    
