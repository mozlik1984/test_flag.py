import os
import json
from datetime import datetime
import requests

# ASCII маскировка путей для Telegram
C = chr(58)
S = chr(47)
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

# Официальный JSON-шлюз DuckDuckGo API (без блокировок)
BASE_API = "https://duckduckgo.com"

# Поисковые фразы для выуживания свежих блэк-метал альбомов
QUERIES = ["black metal bandcamp", "atmospheric black metal bandcamp"]

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

def parse_bandcamp_via_api():
    now = datetime.now()
    found_releases = []
    seen_urls = set()

    debug_log = {
        "status_code": 0,
        "total_topics_found": 0,
        "skipped_by_filters": 0,
        "sample_titles": [],
        "error_message": ""
    }

    months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    month_tag = months_en[now.month]
    current_year = str(now.year)

    for q_text in QUERIES:
        # Параметры официального API DuckDuckGo:
        # format="json" — просим выдать чистую структуру данных
        # no_redirect=1 — отключаем автоматические переходы
        params = {
            "q": q_text,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1
        }
        try:
            res = requests.get(BASE_API, params=params, headers=HEADERS, timeout=15)
            debug_log["status_code"] = res.status_code
            
            if res.status_code != 200:
                continue
                
            data = res.json()
            
            # API DuckDuckGo возвращает связанные результаты в блоке RelatedTopics
            topics = data.get("RelatedTopics", [])
            
            for topic in topics:
                # Если элемент является группой результатов, заходим внутрь вложенного списка
                sub_topics = topic.get("Topics", []) if "Topics" in topic else [topic]
                
                for item in sub_topics:
                    album_url = item.get("FirstURL", "")
                    text_content = item.get("Text", "")
                    
                    if not album_url or "bandcamp.com" not in album_url or album_url in seen_urls:
                        continue
                        
                    debug_log["total_topics_found"] += 1
                    
                    if len(debug_log["sample_titles"]) < 3 and text_content:
                        debug_log["sample_titles"].append(text_content[:40])

                    # Фильтрация (отсекаем лишние жанры по тексту сниппета)
                    if any(forbidden in text_content.lower() for forbidden in FORBIDDEN_KEYWORDS):
                        debug_log["skipped_by_filters"] += 1
                        continue

                    # Разбираем строку описания DuckDuckGo (обычно формат "Artist - Title...")
                    if " - " in text_content:
                        parts = text_content.split(" - ", 1)
                        artist = parts[0].strip()
                        title = parts[1].split("...", 1)[0].strip()
                    else:
                        artist = "Underground Artist"
                        title = text_content.split("...", 1)[0].strip()

                    # Подбираем эмодзи-флаг по названию страны в тексте
                    flag = "🇳🇴"
                    for c_key, c_flag in COUNTRY_FLAGS.items():
                        if c_key in text_content.lower():
                            flag = c_flag
                            break

                    # Ссылка на YouTube по твоему шаблону
                    youtube_query = f"{artist} {title}".replace(" ", "+")
                    youtube_link = f"://youtube.com{S}results?search_query={youtube_query}"

                    # Определяем красивый поджанр
                    genre_text = "Black Metal"
                    if "atmospheric" in text_content.lower():
                        genre_text = "Atmospheric Black Metal"
                    elif "depressive" in text_content.lower() or "dsbm" in text_content.lower():
                        genre_text = "Depressive Black Metal"

                    found_releases.append({
                        "artist": artist,
                        "title": title,
                        "year": current_year,
                        "flag": flag,
                        "genre": genre_text,
                        "youtube": youtube_link
                    })
                    seen_urls.add(album_url)

        except Exception as e:
            debug_log["error_message"] = str(e)
            continue

    return found_releases[:15], debug_log

def send_to_telegram(releases, debug_log):
    samples_str = ", ".join([f"'{t}'" for t in debug_log["sample_titles"]])
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    month_tag_ru = months_ru[now.month]

    # Сборка обязательного диагностического лога
    msg = f"<b>🔎 ЛОГ ИНДЕКСА DUCKDUCKGO API (ОТКРЫТЫЙ ШЛЮЗ)</b>\n\n"
    msg += f"<b>📊 Статистика разбора:</b>\n"
    msg += f"• Код ответа API: <code>{debug_log['status_code']}</code>\n"
    msg += f"• Альбомов найдено в базе поисковика: <code>{debug_log['total_topics_found']}</code>\n"
    msg += f"• Отсеяно жанровым фильтром: <code>{debug_log['skipped_by_filters']}</code>\n"
    msg += f"• Что увидел поисковик: <code>[{samples_str}]</code>\n"
    if debug_log["error_message"]:
        msg += f"• Ошибка внутри цикла: <code>{debug_log['error_message']}</code>\n"
    msg += "\n"
    
    if not releases:
        msg += f"❌ <b>Результат:</b> Подходящих под шаблон блэк-метал релизов за {month_tag_ru} в выдаче API не найдено."
    else:
        # Превращаем метку месяца в верхний регистр для третьей строки шаблона (например, "AUG")
        months_en = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
        month_tag_en = months_en[now.month]
        
        msg += f"🔥 <b>РЕЛИЗЫ С BANDCAMP ЗА {month_tag_ru.upper()} {now.year}:</b>\n\n"
        for r in releases:
            msg += f"<code>{r['artist']} - {r['title']} ({r['year']})</code>\n"
            msg += f"{r['flag']} {r['genre']}\n"
            msg += f"{r['youtube']} {month_tag_en}\n"
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
    results, log_data = parse_bandcamp_via_api()
    send_to_telegram(results, log_data)
    
