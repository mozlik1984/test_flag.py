import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

# Жесткое правило: сборка служебных символов через ASCII
# d = '.', c = ':', s = '/'
d = chr(46)
c = chr(58)
s = chr(47)

# Посимвольная монолитная сборка прокси-домена: https://codetabs.com
PROXY_DOM = f"https{c}{s}{s}api{d}codetabs{d}com{s}cors-proxy{s}"

# ИСПРАВЛЕНО: Все слеши строго маленькой буквой {s}! https://bandcamp.com
FEED_DOM = f"https{c}{s}{s}bandcamp{d}com{s}feed{s}tag{s}"

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

def parse_bandcamp_rss_cascade():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    
    # Карта отладки (ВСЕГДА отправляется в Telegram)
    debug_log = {
        "status_code": 0,
        "raw_text_length": 0,
        "total_xml_entries": 0,
        "skipped_by_filters": 0,
        "error_message": "",
        "sample_titles": []
    }

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for tag in BLACK_METAL_TAGS:
        target_url = f"{FEED_DOM}{tag}"
        full_proxy_url = f"{PROXY_DOM}{target_url}"
        
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(full_proxy_url, headers=headers, timeout=20)
            
            if debug_log["status_code"] == 0:
                debug_log["status_code"] = res.status_code
                debug_log["raw_text_length"] = len(res.text)

            if res.status_code != 200 or not res.text:
                continue
                
            root = ET.fromstring(res.text)
            ns = {'atom': 'http://w3.org'}
            entries = root.findall('atom:entry', ns)
            
            debug_log["total_xml_entries"] += len(entries)
            
            for entry in entries:
                title_tag = entry.find('atom:title', ns)
                link_tag = entry.find('atom:link', ns)
                
                if title_tag is None or link_tag is None:
                    continue
                    
                title_text = title_tag.text.strip()
                album_url = link_tag.attrib.get('href', '')
                
                if not album_url or album_url in seen_urls:
                    continue
                    
                if len(debug_log["sample_titles"]) < 3:
                    debug_log["sample_titles"].append(title_text[:40])

                if any(forbidden in title_text.lower() for forbidden in FORBIDDEN_KEYWORDS):
                    debug_log["skipped_by_filters"] += 1
                    continue

                if " by " in title_text:
                    title, artist = title_text.rsplit(" by ", 1)
                else:
                    title, artist = title_text, "Underground Artist"

                flag = "🇳🇴"  # Тру-дефолт
                summary_tag = entry.find('atom:summary', ns)
                summary_text = summary_tag.text.lower() if summary_tag is not None else ""
                
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in summary_text or c_key in title_text.lower():
                        flag = c_flag
                        break

                genre_text = tag.replace("-", " ").title()

                found_releases.append({
                    "artist": artist.strip(),
                    "title": title.strip(),
                    "year": current_year,
                    "flag": flag,
                    "genre": genre_text,
                    "month": month_tag
                })
                seen_urls.add(album_url)

        except Exception as e:
            if not debug_log["error_message"]:
                debug_log["error_message"] = str(e)
            continue
            
    return found_releases[:15], debug_log

def send_to_telegram(releases, debug_log):
    samples_str = ", ".join([f"'{t}'" for t in debug_log["raw_titles_sample"]])
    
    msg = f"<b>🔎 ПОСТОЯННЫЙ ЛОГ ОТЛАДКИ RSS-FEED</b>\n\n"
    msg += f"<b>📊 Метрики шлюза:</b>\n"
    msg += f"• Код ответа прокси: <code>{debug_log['status_code']}</code>\n"
    msg += f"• Получено символов XML: <code>{debug_log['raw_text_length']}</code>\n"
    msg += f"• Записей найдено в фидах: <code>{debug_log['total_xml_entries']}</code>\n"
    msg += f"• Отсеяно фильтром поджанров: <code>{debug_log['skipped_by_filters']}</code>\n"
    msg += f"• Что прислал фид (сырые строки): <code>[{samples_str}]</code>\n"
    if debug_log["error_message"]:
        msg += f"• Ошибка внутри кода: <code>{debug_log['error_message']}</code>\n"
    msg += "\n"
    
    if not releases:
        msg += "❌ <b>Результат фильтра:</b> Живых блэк-метал новинок по критериям в фиде не обнаружено."
    else:
        msg += "🔥 <b>НОВЫЕ ЖИВЫЕ РЕЛИЗЫ С BANDCAMP:</b>\n\n"
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
    results, log_data = parse_bandcamp_rss_cascade()
    send_to_telegram(results, log_data)
    
