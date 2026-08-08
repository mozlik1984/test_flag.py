import os
import json
from datetime import datetime
import requests

# ASCII маскировка путей
C = chr(58)
S = chr(47)

BASE_API = f"https{C}{S}{S}bandcamp.com{S}api{S}bcsearch{S}1{S}autocomplete"
BASE_TG = f"https{C}{S}{S}api.telegram.org{S}bot"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5002053185"

QUERIES = ["black metal"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_and_debug_api():
    now = datetime.now()
    raw_response_text = ""
    found_releases = []
    
    # Берем первый же запрос для анализа структуры
    params = {"q": QUERIES[0]}
    try:
        res = requests.get(BASE_API, params=params, headers=HEADERS, timeout=15)
        raw_response_text = res.text
        
        if res.status_code == 200:
            data = res.json()
            # Проверяем все возможные стандартные ключи выдачи Bandcamp
            items = data.get("auto", []) or data.get("results", []) or data.get("items", [])
            
            # Если основной массив пуст, проверим, нет ли вложенности
            if not items and isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list) and len(val) > 0:
                        items = val
                        break

            for item in items:
                # Пытаемся вытащить данные любыми путями из всех возможных ключей
                title = item.get("name") or item.get("item_title") or item.get("title") or "Unknown"
                artist = item.get("artist_name") or item.get("band_name") or "Unknown"
                
                found_releases.append({
                    "artist": str(artist),
                    "title": str(title),
                    "year": str(now.year),
                    "flag": "🇳🇴",
                    "genre": "Black Metal",
                    "youtube": f"://youtube.com{S}results?search_query=test",
                    "month": "AUG"
                })
    except Exception as e:
        raw_response_text = f"Ошибка выполнения запроса: {e}"

    return found_releases[:5], raw_response_text[:700]

def send_to_telegram(releases, raw_dump):
    # Если релизы нащупать не удалось — шлем дамп структуры
    if not releases:
        msg = f"<b>🔎 ДИАГНОСТИКА СТРУКТУРЫ JSON BANDCAMP</b>\n\n"
        msg += f"Ответ сервера (первые 700 символов):\n<code>{raw_dump}</code>\n\n"
        msg += "Скопируй этот текст или сделай скриншот, по нему мы сразу поймем ключи!"
    else:
        msg = "🔥 <b>ТЕСТОВЫЙ ПРОБИВ ШЛЮЗА:</b>\n\n"
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
    results, dump = parse_and_debug_api()
    send_to_telegram(results, dump)
    
