import os
import json
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

FORBIDDEN_TAGS = ["thrash-metal", "death-metal", "heavy-metal", "power-metal", "metalcore"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_debug():
    now = datetime.now()
    found_releases = []
    seen_urls = set()
    
    # Словари для детальной отладки в Telegram
    debug_log = {
        "total_raw_items": 0,
        "skipped_by_forbidden_tags": 0,
        "skipped_by_date_mismatch": 0,
        "date_parse_errors": 0,
        "sample_dates": [] # Сюда сохраним примеры дат с сайта
    }

    for tag in BLACK_METAL_TAGS:
        url = f"{BASE_BC}{tag}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            pagedata_tag = soup.find("div", id="pagedata") or soup.find("script", {"id": "pagedata"})
            if not pagedata_tag:
                continue
                
            data = json.loads(pagedata_tag.get("data-blob") or pagedata_tag.text)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                debug_log["total_raw_items"] += 1
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                item_tags = [t.lower() for t in item.get("tags", [])]
                if any(forbidden in item_tags for forbidden in FORBIDDEN_TAGS):
                    debug_log["skipped_by_forbidden_tags"] += 1
                    continue
                
                clean_url = album_url.split('?')[0] if '?' in album_url else album_url
                rel_date_str = item.get("release_date")
                
                if rel_date_str:
                    # Сохраняем примеры оригинальных строк дат для анализа
                    if len(debug_log["sample_dates"]) < 5 and rel_date_str not in debug_log["sample_dates"]:
                        debug_log["sample_dates"].append(rel_date_str)
                        
                    try:
                        # Пытаемся распарсить дату ("05 Aug 2026")
                        rel_date = datetime.strptime(rel_date_str, "%d %b %Y")
                        if rel_date.month == now.month and rel_date.year == now.year:
                            found_releases.append({
                                "artist": item.get("artist"),
                                "title": item.get("title"),
                                "url": clean_url
                            })
                            seen_urls.add(album_url)
                        else:
                            debug_log["skipped_by_date_mismatch"] += 1
                    except Exception:
                        debug_log["date_parse_errors"] += 1
                        # В случае ошибки парсинга — временно забираем в улов, чтобы не потерять
                        found_releases.append({
                            "artist": item.get("artist"),
                            "title": item.get("title") + " (⚠️ Дата не распознана)",
                            "url": clean_url
                        })
                        seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка тега {tag}: {e}")
            continue
            
    return found_releases[:15], debug_log

def send_to_telegram(releases, debug_log):
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    now = datetime.now()
    
    # Формируем блок диагностики
    dates_str = ", ".join([f"'{d}'" for d in debug_log["sample_dates"]])
    
    msg = f"<b>🇳🇴 БЛЭК-МЕТАЛ УЛОВ И ОТЛАДКА</b>\n"
    msg += f"Период фильтра: <code>{months_ru[now.month]} {now.year}</code>\n\n"
    msg += f"<b>📊 Статистика этапов:</b>\n"
    msg += f"• Всего релизов найдено в API: <code>{debug_log['total_raw_items']}</code>\n"
    msg += f"• Отсеяно по запрещенным тегам: <code>{debug_log['skipped_by_forbidden_tags']}</code>\n"
    msg += f"• Не подошли по месяцу/году: <code>{debug_log['skipped_by_date_mismatch']}</code>\n"
    msg += f"• Ошибок распознавания даты: <code>{debug_log['date_parse_errors']}</code>\n"
    msg += f"• Примеры дат с сайта: <code>[{dates_str}]</code>\n\n"
    
    if not releases:
        msg += "❌ <b>Результат:</b> Подходящих релизов не найдено."
    else:
        msg += "🔥 <b>Найденные релизы:</b>\n\n"
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
    results, log_data = parse_bandcamp_debug()
    send_to_telegram(results, log_data)
    
