import os
import urllib.request
import urllib.parse
import json
import time
import sys

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Безопасная ASCII-склейка для защиты от искажений на мобильном
S = chr(47); C = chr(58); Q = chr(63); E = chr(61)
P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿"
}

COUNTRY_MAP = {
    "NO": "Norway", "SE": "Sweden", "FI": "Finland", "DE": "Germany", 
    "FR": "France", "US": "United States", "GB": "United Kingdom", 
    "UA": "Ukraine", "RU": "Russia", "AT": "Austria", "IS": "Iceland", 
    "PL": "Poland", "GR": "Greece", "IT": "Italy", "CH": "Switzerland", 
    "NL": "Netherlands", "AU": "Australia", "CA": "Canada", "BR": "Brazil", "JP": "Japan"
}

def fetch_musicbrainz_new_arrivals():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    
    user_corrections = ""
    
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        if len(sys.argv) > 3: user_corrections = str(sys.argv[3]).strip()
        
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print(f"🛰️ Поиск релизов за цель: {current_month_tag} {current_year}")
    
    query = f'type:album AND status:official AND date:{current_year} AND tag:"black metal"'
    url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&inc=tags+artist-credits&fmt=json&limit=100"
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
                    rel_date = rel.get("date", "")
                    if rel_date:
                        date_parts = rel_date.split("-")
                        if len(date_parts) > 1:
                            if date_parts[1] != current_month_num:
                                continue

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
                        
                        tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
                        tags_str = " ".join(tags_list)
                        
                        subgenres = []
                        if "hellenic" in tags_str or "greece" in tags_str: subgenres.append("Hellenic Black Metal")
                        if "atmospheric" in tags_str: subgenres.append("Atmospheric Black Metal")
                        if "depressive" in tags_str or "dsbm" in tags_str: subgenres.append("Depressive Black Metal")
                        if "post-black" in tags_str: subgenres.append("Post-Black Metal")
                        if "psychedelic" in tags_str: subgenres.append("Psychedelic Black Metal")
                        if "symphonic" in tags_str: subgenres.append("Symphonic Black Metal")
                        if "raw" in tags_str: subgenres.append("Raw Black Metal")
                        if "melodic" in tags_str: subgenres.append("Melodic Black Metal")
                        if "old school" in tags_str or "first wave" in tags_str: subgenres.append("Old School Black Metal")
                        
                        detected_subgenre = "/".join(subgenres) if subgenres else "Black Metal"
                        
                        country_code = rel.get("country", "")
                        if (not country_code or country_code == "XW") and artist_id:
                            try:
                                artist_url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "artist" + S + artist_id + "?inc=aliases&fmt=json"
                                req_art = urllib.request.Request(artist_url, headers=headers)
                                with urllib.request.urlopen(req_art, timeout=5) as res_art:
                                    art_data = json.loads(res_art.read().decode('utf-8'))
                                    country_code = art_data.get("country", "")
                                    if not country_code:
                                        area_data = art_data.get("area", {})
                                        iso = area_data.get("iso-3166-1-codes", [])
                                        if iso: country_code = iso[0]
                                time.sleep(0.5)
                            except: pass

                        country_name = COUNTRY_MAP.get(str(country_code).upper(), "")
                        flag = COUNTRY_TO_FLAG.get(country_name, "")
                        
                        is_deleted = False
                        if user_corrections and user_corrections != "AUTO":
                            rules = user_corrections.split(",")
                            for rule in rules:
                                if "=" in rule:
                                    k, v = rule.split("=", 1)
                                    if k.strip().lower() in band.lower() and "delete" in v.lower(): 
                                        is_deleted = True
                        
                        if is_deleted: continue
                        flag_prefix = flag + " " if flag else ""
                        yt_link = "https" + C + S + S + "youtube.com" + S + "results" + Q + "search_query" + E + urllib.parse.quote(band + " " + album)
                        
                        block = f"{band} - {album} ({current_year})\n{flag_prefix}{detected_subgenre}\n{yt_link} {current_month_tag}"
                        packs.append(block)
                        
                if packs:
                    return "\n---\n".join(packs)
                    
        return f"🌑 Проверенных полноформатных новинок за {current_month_tag} {current_year} пока не зафиксировано."
    except Exception as e:
        return "❌ Ошибка агрегатора: " + str(e)

def send_to_admin(content_text, month_tag, year_val):
    if not BOT_TOKEN:
        print("Ошибка: Токен Telegram не найден.")
        return
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ ЧИСТЫЙ АВТОНОМНЫЙ УЛОВ ЗА {month_tag} {year_val} ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Ложные флаги отключены. Если страны нет в базе, альбом запишется чистым! Тапни для копирования.</i>"
    
    data = urllib.parse.urlencode({
        'chat_id': ADMIN_CHAT_ID, 
        'text': formatted_msg, 
        'parse_mode': 'HTML',
        'link_preview_options': json.dumps({'is_disabled': True})
    }).encode('utf-8')
    
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

    
