import os
import urllib.request
import urllib.parse
import json
import time
import sys
import re

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Фирменная безопасная ASCII-склейка для защиты от искажений на мобильном
S = chr(47); C = chr(58)
Q = chr(63); E = chr(61)  # ИСПРАВЛЕНО: Добавлены знаки ? (Q) и = (E)
P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴🇺"
}

COUNTRY_MAP = {
    "NO": "Norway", "SE": "Sweden", "FI": "Finland", "DE": "Germany", 
    "FR": "France", "US": "United States", "GB": "United Kingdom", 
    "UA": "Ukraine", "RU": "Russia", "AT": "Austria", "IS": "Iceland", 
    "PL": "Poland", "GR": "Greece", "IT": "Italy", "CH": "Switzerland", 
    "NL": "Netherlands", "AU": "Australia"
}

def fetch_musicbrainz_new_arrivals():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    
    user_corrections = ""
    
    # Исправлено безопасное считывание параметров с экрана GitHub
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        if len(sys.argv) > 3: user_corrections = str(sys.argv[3]).strip()
        
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print("🛰️ Поиск в архивах MusicBrainz по цели: " + current_month_tag + " " + str(current_year))
    
    # Строим строгий поисковый запрос к базе данных релизов
    query = 'type:album AND status:official AND date:' + str(current_year) + '-' + current_month_num + ' AND tag:"black metal"'
    url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&inc=tags+artist-credits&fmt=json&limit=30"
    
    headers = {'User-Agent': 'BlackMetalHubBot/17.0 ( mailto:Plokhomentov@example.com )'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                releases = data.get("releases", [])
                
                packs = []
                seen_albums = set()
                
                for rel in releases:
                    artist_credit = rel.get("artist-credit", [])
                    if not artist_credit: continue
                    
                    first_artist = artist_credit[0] if isinstance(artist_credit, list) else artist_credit
                    artist_data = first_artist.get("artist", {})
                    
                    band = artist_data.get("name", "").strip()
                    album = rel.get("title", "").strip()
                    artist_id = artist_data.get("id", "")
                    
                    if band and album:
                        release_key = band.lower() + " - " + album.lower()
                        if release_key in seen_albums: continue
                        seen_albums.add(release_key)
                        
                        # Автоматическое определение поджанров по тегам базы
                        tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
                        tags_str = " ".join(tags_list)
                        detected_subgenre = "Black Metal"
                        if "atmospheric" in tags_str: detected_subgenre = "Atmospheric Black Metal"
                        elif "depressive" in tags_str or "dsbm" in tags_str: detected_subgenre = "Depressive Black Metal"
                        elif "post-black" in tags_str: detected_subgenre = "Post-Black Metal"
                        elif "psychedelic" in tags_str: detected_subgenre = "Psychedelic Black Metal"
                        elif "symphonic" in tags_str: detected_subgenre = "Symphonic Black Metal"
                        
                        # Поиск страны
                        country_code = rel.get("country", "")
                        if (not country_code or country_code == "XW") and artist_id:
                            try:
                                artist_url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "artist" + S + artist_id + "?fmt=json"
                                req_art = urllib.request.Request(artist_url, headers=headers)
                                with urllib.request.urlopen(req_art, timeout=5) as res_art:
                                    art_data = json.loads(res_art.read().decode('utf-8'))
                                    country_code = art_data.get("country", "")
                                time.sleep(0.5)
                            except: pass

                        country_name = COUNTRY_MAP.get(str(country_code).upper(), "")
                        flag = COUNTRY_TO_FLAG.get(country_name, "")
                        
                        # Админские ручные правки удаления
                        is_deleted = False
                        if user_corrections and user_corrections != "AUTO":
                            rules = user_corrections.split(",")
                            for rule in rules:
                                if "=" in rule:
                                    k, v = rule.split("=", 1)
                                    if k.strip().lower() in band.lower():
                                        if "delete" in v.lower(): is_deleted = True
                        
                        if is_deleted: continue
                        
                        flag_prefix = flag + " " if flag else ""
                        
                        # Ссылка-заглушка на поиск в YouTube (ИСПРАВЛЕНО)
                        yt_link = P + "www.youtube.com" + S + "results" + Q + "search_query" + E + urllib.parse.quote(band + " " + album)
                        
                        block = band + " - " + album + " (" + str(current_year) + ")\n" + flag_prefix + detected_subgenre + "\n" + yt_link + " " + current_month_tag
                        packs.append(block)
                        
                if packs:
                    return "\n---\n".join(packs)
                    
        return "🌑 Проверенных полноформатных новинок за " + current_month_tag + " " + str(current_year) + " пока не зафиксировано."
    except Exception as e:
        return "❌ Ошибка агрегатора: " + str(e)

def send_to_admin(content_text, month_tag, year_val):
    if not BOT_TOKEN:
        print("Ошибка: Токен Telegram (TELEGRAM_TOKEN) не найден в переменных окружения.")
        return
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = "<b>⛓️ ЧИСТЫЙ АВТОНОМНЫЙ УЛОВ ЗА " + month_tag + " " + str(year_val) + " ⛓️</b>\n\n<code>" + content_text + "</code>\n\n<i>👉 Ложные флаги отключены. Если страны нет в базе, альбом запишется чистым! Тапни для копирования.</i>"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print("Ошибка отправки в Telegram:", e)

if __name__ == "__main__":
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    time_struct = time.gmtime()
    m_tag = months_map.get(time_struct.tm_mon, "JUL")
    y_val = time_struct.tm_year
    
    if len(sys.argv) > 2 and str(sys.argv[1]).upper() != "AUTO": m_tag = str(sys.argv[1]).upper()
    if len(sys.argv) > 2 and str(sys.argv[2]) != "AUTO": y_val = str(sys.argv[2])
    
    final_report = fetch_musicbrainz_new_arrivals()
    send_to_admin(final_report, m_tag, y_val)
                
