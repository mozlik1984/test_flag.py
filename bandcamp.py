import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ASCII маскировка путей для Telegram
C = chr(58)
S = chr(47)
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Прямая ссылка без капризной ASCII сборки — DuckDuckGo Гитхаб не блокирует!
BASE_DDG = "https://duckduckgo.com"

QUERIES = [
    'site:bandcamp.com "black metal" "album" "2026"',
    'site:bandcamp.com "atmospheric black metal" "2026"'
]

FORBIDDEN_KEYWORDS = ["thrash", "death", "heavy", "power", "core", "electronic", "punk"]

COUNTRY_FLAGS = {
    "norway": "🇳🇴", "sweden": "🇸🇪", "finland": "🇫🇮", "france": "🇫🇷",
    "germany": "🇩🇪", "usa": "🇺🇸", "united states": "🇺🇸", "ukraine": "🇺🇦", 
    "poland": "🇵🇱", "austria": "🇦🇹", "italy": "🇮🇹", "canada": "🇨🇦", 
    "iceland": "🇮🇸", "greece": "🇬🇷", "russia": "🇷🇺", "united kingdom": "🇬🇧"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_via_search_index():
    now = datetime.now()
    found_releases = []
    seen_identities = set()

    debug_log = {
        "status_code": 0,
        "total_results_found": 0,
        "skipped_by_filters": 0,
        "raw_titles_sample": [],
        "error_message": ""
    }

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for q_text in QUERIES:
        payload = {"q": q_text}
        try:
            res = requests.post(BASE_DDG, data=payload, headers=HEADERS, timeout=20)
            debug_log["status_code"] = res.status_code
            
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            results = soup.find_all("div", class_="result__body")
            
            for item in results:
                title_tag = item.find("a", class_="result__url")
                if not title_tag:
                    continue
                    
                raw_title = title_tag.text.strip()
                if not raw_title or "duckduckgo" in raw_title.lower():
                    continue
                    
                debug_log["total_results_found"] += 1
                
                if len(debug_log["raw_titles_sample"]) < 3:
                    debug_log["raw_titles_sample"].append(raw_title)

                snippet_tag = item.find("a", class_="result__snippet")
                snippet_text = snippet_tag.text.strip().lower() if snippet_tag else ""
                
                # Безопасный разбор строк без падения цикла
                if " | " in raw_title:
                    parts = raw_title.split(" | ")
                    title = parts[0].strip()
                    artist = parts[1].replace("Bandcamp", "").strip() if len(parts) > 1 else "Underground Artist"
                elif " - " in raw_title:
                    parts = raw_title.split(" - ", 1)
                    artist = parts[0].strip()
                    title = parts[1].replace("Bandcamp", "").strip() if len(parts) > 1 else "Release"
                else:
                    title = raw_title
                    artist = "Underground Artist"

                full_desc = f"{title} {artist} {snippet_text}".lower()
                if any(forbidden in full_desc for forbidden in FORBIDDEN_KEYWORDS):
                    debug_log["skipped_by_filters"] += 1
                    continue
                    
                full_identity = f"{artist} - {title}".lower()
                if full_identity in seen_identities:
                    continue

                flag = "🇳🇴"
                for c_key, c_flag in COUNTRY_FLAGS.items():
                    if c_key in full_desc:
                        flag = c_flag
                        break

                youtube_query = f"{artist} {title}".replace(" ", "+")
                youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                genre_text = "Black Metal"
                if "atmospheric" in full_desc:
                    genre_text = "Atmospheric Black Metal"
                elif "depressive" in full_desc or "dsbm" in full_desc:
                    genre_text = "Depressive Black Metal"

                found_releases.append({
                    "artist": artist,
                    "title": title,
                    "year": current_year,
                    "flag": flag,
                    "genre": genre_text,
                    "youtube": youtube_link,
                    "month": month_tag
                })
                seen_identities.add(full_identity)

        except Exception as e:
            debug_log["error_message"] = str(e)
            continue

    return found_releases[:15], debug_log

def send_to_telegram(releases, debug_log):
    samples_str = ", ".join([f"'{t}'" for t in debug_log["raw_titles_sample"]])
    
    msg = f"<b>🔎 ЛОГ ИНДЕКСА ПОИСКОВИКА (БЕЗ БЛОКИРОВОК)</b>\n\n"
    msg += f"<b>📊 Статистика разбора:</b>\n"
    msg += f"• Код ответа DuckDuckGo: <code>{debug_log['status_code']}</code>\n"
    msg += f"• Ссылок обнаружено в верстке: <code>{debug_log['total_results_found']}</code>\n"
    msg += f"• Отсеяно жанровым фильтром: <code>{debug_log['skipped_by_filters']}</code>\n"
    msg += f"• Что увидел поисковик: <code>[{samples_str}]</code>\n"
    if debug_log["error_message"]:
        msg += f"• Ошибка внутри цикла: <code>{debug_log['error_message']}</code>\n"
    msg += "\n"
    
    if not releases:
        msg += "❌ <b>Результат:</b> Подходящих под шаблон блэк-метал релизов в этой выдаче не найдено."
    else:
        msg += "🔥 <b>РЕЛИЗЫ С BANDCAMP ПО ТВОЕМУ ШАБЛОНУ:</b>\n\n"
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
    results, log_data = parse_bandcamp_via_search_index()
    send_to_telegram(results, log_data)
    
