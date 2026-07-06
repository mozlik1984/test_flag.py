import os
import urllib.request
import urllib.parse
import json
import time
import sys

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58); Q = chr(63); E = chr(61)
P = "https" + C + S + S

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
    "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Estonia": "🇪🇪"
}

COUNTRY_MAP = {
    "NO": "Norway", "SE": "Sweden", "FI": "Finland", "DE": "Germany", 
    "FR": "France", "US": "United States", "GB": "United Kingdom", 
    "UA": "Ukraine", "RU": "Russia", "AT": "Austria", "IS": "Iceland", 
    "PL": "Poland", "GR": "Greece", "IT": "Italy", "CH": "Switzerland", 
    "NL": "Netherlands", "AU": "Australia", "CA": "Canada", "BR": "Brazil", 
    "JP": "Japan", "CZ": "Czech Republic", "DK": "Denmark", "ID": "Indonesia", 
    "HU": "Hungary", "IE": "Ireland", "CO": "Colombia", "CL": "Chile", 
    "AR": "Argentina", "MX": "Mexico", "NZ": "New Zealand", "SK": "Slovakia", 
    "SI": "Slovenia", "EE": "Estonia"
}

def fetch_musicbrainz_new_arrivals():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    user_corrections = ""
    
    # Безопасное чтение аргументов командной строки
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        
        if len(sys.argv) > 3: 
            user_corrections = str(sys.argv[3]).strip()
        
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print(f"🛰️ Поиск релизов за период: {current_month_tag} {current_year}")
    
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
    
    for i in range(0, len(genres), chunk_size):
        chunk = genres[i:i + chunk_size]
        tag_queries = " OR ".join([f'tag:"{g}"' for g in chunk])
        
        query = f'type:album AND status:official AND date:{current_year} AND ({tag_queries})'
        url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&inc=tags+artist-credits&fmt=json&limit=100"
        headers = {'User-Agent': 'BlackMetalHubBot/17.0 ( mailto:Plokhomentov@example.com )'}
        
        time.sleep(1) # Соблюдаем Rate Limit
        
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
            else:
                print(f"⚠️ Ошибка: Сервер MusicBrainz перегружен (503) на группе жанров {chunk}.")
                continue
        except Exception as e:
            print(f"⚠️ Ошибка при поиске группы {chunk}: {e}")
            continue

    # Блок обработки результатов (вынесен из цикла запросов)
    packs = []
    seen_albums = set()
    
    for rel in all_releases:
        rel_date = rel.get("date", "")
        if rel_date:
            date_parts = rel_date.split("-")
            if len(date_parts) > 1:
                if date_parts[1] != current_month_num:
                    continue

        artist_credit = rel.get("artist-credit", [])
        if not artist_credit: 
            continue
        
        first_artist = artist_credit[0] if isinstance(artist_credit, list) else artist_credit
        artist_data = first_artist.get("artist", {})
        band = artist_data.get("name", "").strip()
        album = rel.get("title", "").strip()
        
        # Получаем код страны из профиля группы и переводим его в флаг
        country_code = artist_data.get("country", "")
        flag_emoji = ""
        if country_code:
            country_name = COUNTRY_MAP.get(country_code.upper())
            if country_name:
                flag_emoji = COUNTRY_TO_FLAG.get(country_name, "")
        
        if band and album:
            release_key = band.lower() + " - " + album.lower()
            if release_key in seen_albums: 
                continue
            seen_albums.add(release_key)
            
            tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
            
            subgenres = []
            for g_tag, g_name in genres_map.items():
                if g_tag in tags_list:
                    if g_name not in subgenres:
                        subgenres.append(g_name)
            
            if not subgenres:
                subgenres = ["Black Metal"]
                
            genre_str = "/".join(subgenres)
            
            # Подставляем флаг перед строкой жанров (если он нашелся)
            prefix = f"{flag_emoji} " if flag_emoji else ""
            
            release_info = f"{band} - {album} ({current_year})\n{prefix}{genre_str}\nhttps://youtube.com {current_month_tag}"
            packs.append(release_info)

    # Отправка результатов в Telegram
    if not packs:
        output_text = f"🤷 За {current_month_tag} {current_year} релизов не найдено."
    else:
        output_text = f"\n---\n".join(packs)

    # Разбивка длинных сообщений под лимиты Telegram
    max_len = 4000
    for chunk_text in [output_text[i:i + max_len] for i in range(0, len(output_text), max_len)]:
        send_url = f"{P}api.telegram.org{S}bot{BOT_TOKEN}{S}sendMessage"
        payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": chunk_text}).encode('utf-8')
        req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                pass
        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")

if __name__ == "__main__":
    fetch_musicbrainz_new_arrivals()
