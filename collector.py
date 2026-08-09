import os
import sys
import json
import urllib.request
from datetime import datetime

# Подтягиваем скрытые секреты из GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USER_COOKIES = os.getenv("BANDCAMP_COOKIES")

BANDCAMP_DISCOVER_URL = "https://bandcamp.com"

COUNTRY_FLAGS = {
    "united states": "🇺🇸", "usa": "🇺🇸", "us": "🇺🇸", "germany": "🇩🇪", "de": "🇩🇪",
    "norway": "🇳🇴", "no": "🇳🇴", "france": "🇫🇷", "fr": "🇫🇷", "poland": "🇵🇱", "pl": "🇵🇱",
    "sweden": "🇸🇪", "se": "🇸🇪", "finland": "🇫🇮", "fi": "🇫🇮", "ukraine": "🇺🇦", "uk": "🇬🇧",
}

def escape_html(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def get_flag_and_clean_location(location_str: str) -> str:
    if not location_str: return ""
    loc_lower = location_str.lower()
    for country, flag in COUNTRY_FLAGS.items():
        if country in loc_lower: return flag + " "
    return ""

def format_genres(tags_list, fallback_genres=None) -> str:
    if not tags_list: tags_list = fallback_genres if fallback_genres else ["Black Metal"]
    cleaned_tags = []
    for tag in tags_list:
        tag_str = str(tag).title()
        if "Black Metal" in tag_str or "Metal" in tag_str:
            if tag_str not in cleaned_tags: cleaned_tags.append(tag_str)
    return "/".join(cleaned_tags) if cleaned_tags else "Black Metal"

def send_to_telegram(text: str):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("ok"):
                print("[+] Порция успешно доставлена в Telegram!")
    except Exception as e:
        print(f"[-] Ошибка отправки в TG: {e}")

def main():
    print("[*] Авторизованный запрос к API Bandcamp через GitHub Cloud...")
    
    req = urllib.request.Request(
        BANDCAMP_DISCOVER_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": USER_COOKIES,
            "Accept": "application/json, text/plain, *.*"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw_output = response.read().decode("utf-8")
            data = json.loads(raw_output)
    except Exception as e:
        print(f"[-] Cloudflare отклонил облачный запрос: {e}")
        return

    items = data.get("items", [])
    if not items:
        print("[-] Релизов не найдено.")
        return

    print(f"[+] Распарсено {len(items)} релизов. Отправка частями...")
    chunks, current_chunk, msg_counter = [], "", 0

    for item in items:
        artist = escape_html(item.get("artist_name", "Unknown Artist"))
        title = escape_html(item.get("album_title") or item.get("title") or "Unknown Album")
        publish_date_raw = item.get("publish_date") or item.get("sc_publish_date")
        month_str, year_str = "AUG", "2026"
        
        if publish_date_raw:
            try:
                dt = datetime.fromtimestamp(publish_date_raw) if isinstance(publish_date_raw, (int, float)) else datetime.strptime(str(publish_date_raw)[:10], "%Y-%m-%d")
                month_str, year_str = dt.strftime("%b").upper(), dt.strftime("%Y")
            except: pass

        flag_prefix = get_flag_and_clean_location(item.get("artist_location", ""))
        genres_line = escape_html(format_genres(item.get("tags", []), [item.get("genre")] if item.get("genre") else None))

        current_chunk += f"<code>{artist} - {title} ({year_str})</code>\n{flag_prefix}{genres_line}\nhttps://youtube.com {month_str}\n---\n"
        msg_counter += 1
        
        if msg_counter >= 5:
            chunks.append(current_chunk)
            current_chunk, msg_counter = "", 0
            
    if current_chunk: chunks.append(current_chunk)

    for chunk in chunks:
        send_to_telegram(chunk)

if __name__ == "__main__":
    main()
  
