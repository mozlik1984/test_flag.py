import os
import urllib.request
import urllib.parse
import json
import time
import sys

# Настройки бота и администратора
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58)
P = "https" + C + S + S

# Расширенный список эмодзи флагов (80 стран)
COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰", 
    "Indonesia": "🇮🇩", "Hungary": "🇭🇺", "Ireland": "🇮🇪", "Colombia": "🇨🇴",
    "Chile": "🇨🇱", "Argentina": "🇦🇷", "Mexico": "🇲🇽", "New Zealand": "🇳🇿",
    "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Estonia": "🇪🇪",
    # Добавленные страны:
    "Belarus": "🇧🇾", "Kazakhstan": "🇰🇿", "Armenia": "🇦🇲", "Georgia": "🇬🇪",
    "Lithuania": "🇱🇹", "Latvia": "🇱🇻", "Romania": "🇷🇴", "Bulgaria": "🇧🇬",
    "Serbia": "🇷🇸", "Croatia": "🇭🇷", "Bosnia and Herzegovina": "🇧🇦", "Montenegro": "🇲🇪",
    "North Macedonia": "🇲🇰", "Albania": "🇦🇱", "Turkey": "🇹🇷", "Cyprus": "🇨🇾",
    "China": "🇨🇳", "Taiwan": "🇹🇼", "South Korea": "🇰🇷", "India": "🇮🇳",
    "Thailand": "🇹🇭", "Vietnam": "🇻🇳", "Malaysia": "🇲🇾", "Singapore": "🇸🇬",
    "Israel": "🇮🇱", "Saudi Arabia": "🇸🇦", "United Arab Emirates": "🇦🇪", "Iran": "🇮🇷",
    "South Africa": "🇿🇦", "Egypt": "🇪🇬", "Morocco": "🇲🇦", "Tunisia": "🇹🇳",
    "Peru": "🇵🇪", "Ecuador": "🇪🇨", "Venezuela": "🇻🇪", "Bolivia": "🇧🇴",
    "Uruguay": "🇺🇾", "Paraguay": "🇵🇾", "Costa Rica": "🇨🇷", "Panama": "🇵🇦",
    "Guatemala": "🇬🇹", "Cuba": "🇨🇺", "Puerto Rico": "🇵🇷", "Greenland": "🇬🇱",
    "Luxembourg": "🇱🇺", "Malta": "🇲🇹", "San Marino": "🇸🇲", "Andorra": "🇦🇩"
}

# Расширенный маппинг ISO-кодов (80 стран)
COUNTRY_MAP = {
    "NO": "Norway", "SE": "Sweden", "FI": "Finland", "DE": "Germany", 
    "FR": "France", "US": "United States", "GB": "United Kingdom", 
    "UA": "Ukraine", "RU": "Russia", "AT": "Austria", "IS": "Iceland", 
    "PL": "Poland", "GR": "Greece", "IT": "Italy", "CH": "Switzerland", 
    "NL": "Netherlands", "AU": "Australia", "CA": "Canada", "BR": "Brazil", 
    "JP": "Japan", "CZ": "Czech Republic", "DK": "Denmark", "ID": "Indonesia", 
    "HU": "Hungary", "IE": "Ireland", "CO": "Colombia", "CL": "Chile", 
    "AR": "Argentina", "MX": "Mexico", "NZ": "New Zealand", "SK": "Slovakia", 
    "SI": "Slovenia", "EE": "Estonia",
    # Добавленные ISO-коды:
    "BY": "Belarus", "KZ": "Kazakhstan", "AM": "Armenia", "GE": "Georgia",
    "LT": "Lithuania", "LV": "Latvia", "RO": "Romania", "BG": "Bulgaria",
    "RS": "Serbia", "HR": "Croatia", "BA": "Bosnia and Herzegovina", "ME": "Montenegro",
    "MK": "North Macedonia", "AL": "Albania", "TR": "Turkey", "CY": "Cyprus",
    "CN": "China", "TW": "Taiwan", "KR": "South Korea", "IN": "India",
    "TH": "Thailand", "VN": "Vietnam", "MY": "Malaysia", "SG": "Singapore",
    "IL": "Israel", "SA": "Saudi Arabia", "AE": "United Arab Emirates", "IR": "Iran",
    "ZA": "South Africa", "EG": "Egypt", "MA": "Morocco", "TN": "Tunisia",
    "PE": "Peru", "EC": "Ecuador", "VE": "Venezuela", "BO": "Bolivia",
    "UY": "Uruguay", "PY": "Paraguay", "CR": "Costa Rica", "PA": "Panama",
    "GT": "Guatemala", "CU": "Cuba", "PR": "Puerto Rico", "GL": "Greenland",
    "LU": "Luxembourg", "MT": "Malta", "SM": "San Marino", "AD": "Andorra"
}

# Кэш стран артистов, чтобы избежать капчи и бана
artist_countries_cache = {}

def get_country_by_artist_id(artist_id, headers):
    """Делает точечный запрос, чтобы 100% забрать код страны"""
    if not artist_id:
        return ""
    if artist_id in artist_countries_cache:
        return artist_countries_cache[artist_id]
        
    url = f"{P}musicbrainz.org{S}ws{S}2{S}artist{S}{artist_id}?fmt=json"
    time.sleep(1) # Соблюдаем rate limit
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                country_code = data.get("country", "")
                if not country_code:
                    area = data.get("area", {})
                    codes = area.get("iso-3166-1-codes", [""])
                    country_code = codes[0] if codes else ""
                
                artist_countries_cache[artist_id] = str(country_code).upper()
                return artist_countries_cache[artist_id]
    except Exception as e:
        print(f"⚠️ Ошибка запроса страны для {artist_id}: {e}")
        
    artist_countries_cache[artist_id] = ""
    return ""

def fetch_musicbrainz_new_arrivals():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    
    # Безопасно парсим аргументы
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print(f"🛰️ Поиск за: {current_month_tag} {current_year}")
    
    genres_map = {
        "black metal": "Black Metal", "dsbm": "Depressive Black Metal", 
        "depressive black metal": "Depressive Black Metal", "post-black metal": "Post-Black Metal",
        "atmospheric black metal": "Atmospheric Black Metal", "true black metal": "True Black Metal", 
        "raw black metal": "Raw Black Metal", "orthodox black metal": "Orthodox Black Metal",
        "melodic black metal": "Melodic Black Metal", "symphonic black metal": "Symphonic Black Metal", 
        "ambient black metal": "Ambient Black Metal", "blackgaze": "Blackgaze",
        "avant-garde black metal": "Avant-Garde Black Metal", "progressive black metal": "Progressive Black Metal", 
        "dissonant black metal": "Dissonant Black Metal", "psychedelic black metal": "Psychedelic Black Metal",
        "blackened death metal": "Blackened Death Metal", "war metal": "War Metal", 
        "bestial black metal": "Bestial Black Metal", "blackened thrash metal": "Blackened Thrash Metal",
        "black doom": "Black-Doom", "blackened crust": "Blackened Crust", 
        "blackened hardcore": "Blackened Hardcore", "blackened grindcore": "Blackened Grindcore",
        "pagan black metal": "Pagan Black Metal", "viking black metal": "Viking Black Metal", 
        "folk black metal": "Folk Black Metal", "medieval black metal": "Medieval Black Metal"
    }
    
    genres = list(genres_map.keys())
    all_releases = []
    chunk_size = 4
    headers = {'User-Agent': 'BlackMetalHubBot/17.0 ( mailto:Plokhomentov@example.com )'}
    
    # Загружаем релизы пачками
    for i in range(0, len(genres), chunk_size):
        chunk = genres[i:i + chunk_size]
        tag_queries = " OR ".join([f'tag:"{g}"' for g in chunk])
        query = f'type:album AND status:official AND date:{current_year} AND ({tag_queries})'
        url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&inc=tags+artist-credits&fmt=json&limit=100"
        
        time.sleep(1)
        try:
            for attempt in range(3):
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        if response.status == 200:
                            chunk_data = json.loads(response.read().decode('utf-8'))
                            if "releases" in chunk_data:
                                all_releases.extend(chunk_data["releases"])
                            break
                except urllib.error.HTTPError as he:
                    if he.code == 503 and attempt < 2:
                        time.sleep(3)
                        continue
                    raise he
        except Exception as e:
            print(f"⚠️ Ошибка на группе {chunk}: {e}")
            continue

    packs = []
    seen_albums = set()
    
    # Фильтруем и собираем информацию о релизах
    for rel in all_releases:
        rel_date = rel.get("date", "")
        if rel_date and len(rel_date.split("-")) > 1:
            if rel_date.split("-")[1] != current_month_num:
                continue

        artist_credit = rel.get("artist-credit", [])
        if not artist_credit: 
            continue
            
        first_artist = artist_credit[0] if isinstance(artist_credit, list) else artist_credit
        artist_data = first_artist.get("artist", {})
        band = artist_data.get("name", "").strip()
        album = rel.get("title", "").strip()
        artist_id = artist_data.get("id", "")
        
        if band and album:
            release_key = band.lower() + " - " + album.lower()
            if release_key in seen_albums: 
                continue
            seen_albums.add(release_key)
            
            # Тянем флаг страны через точечный запрос
            country_code = get_country_by_artist_id(artist_id, headers)
            flag_emoji = ""
            if country_code:
                country_name = COUNTRY_MAP.get(country_code)
                if country_name:
                    flag_emoji = COUNTRY_TO_FLAG.get(country_name, "")
            
            tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
            subgenres = [genres_map[g_tag] for g_tag in genres_map if g_tag in tags_list]
            if not subgenres:
                subgenres = ["Black Metal"]
                
            genre_str = "/".join(list(set(subgenres)))
            prefix = f"{flag_emoji} " if flag_emoji else ""
            
            # Собираем итоговую строчку
            release_info = f"{band} - {album} ({current_year})\n{prefix}{genre_str}\nhttps://youtube.com {current_month_tag}"
            packs.append(release_info)

    # Отправка сообщений в Телеграм
    output_text = f"\n---\n".join(packs) if packs else f"🤷 За {current_month_tag} {current_year} релизов не найдено."
    max_len = 4000
    
    for chunk_text in [output_text[i:i + max_len] for i in range(0, len(output_text), max_len)]:
        send_url = f"{P}api.telegram.org{S}bot{BOT_TOKEN}{S}sendMessage"
        payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": chunk_text}).encode('utf-8')
        req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp: pass
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")

if __name__ == "__main__":
    fetch_musicbrainz_new_arrivals()
