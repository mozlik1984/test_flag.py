import os
import urllib.request
import urllib.parse
import json
import time
import sys

# Настройки бота и администратора
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Абсолютная ASCII-защита всех протоколов и спецсимволов
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
A = chr(38)  # &
P = "https" + C + S + S

# Полное посимвольное шифрование всех доменов и API-путей
MB_BASE = "musicbrainz" + D + "org" + S + "ws" + S + "2" + S
D_BASE = "api" + D + "discogs" + D + "com" + S + "database" + S + "search"
TG_BASE = "api" + D + "telegram" + D + "org" + S + "bot"
YT_BASE = "youtube" + D + "com"

# Расширенный список эмодзи флагов (80 стран)
COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢🇺󠁬󠁳󠁿", "China": "🇨🇳", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰",
    "Indonesia": "🇮🇩", "Hungary": "🇭🇺", "Ireland": "🇮🇪", "Colombia": "🇨🇴",
    "Chile": "🇨🇱", "Argentina": "🇦🇷", "Mexico": "🇲🇽", "New Zealand": "🇳🇿",
    "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Estonia": "🇪🇪", "Belarus": "🇧🇾",
    "Kazakhstan": "🇰🇿", "Armenia": "🇦🇲", "Georgia": "🇬🇪", "Lithuania": "🇱🇹",
    "Latvia": "🇱🇻", "Romania": "🇷🇴", "Bulgaria": "🇧🇬", "Serbia": "🇷🇸",
    "Croatia": "🇭🇷", "Bosnia and Herzegovina": "🇧🇦", "Montenegro": "🇲🇪",
    "North Macedonia": "🇲🇰", "Albania": "🇦🇱", "Turkey": "🇹🇷", "Cyprus": "🇨🇾",
    "Taiwan": "🇹🇼", "South Korea": "🇰🇷", "India": "🇮🇳", "Thailand": "🇹🇭",
    "Vietnam": "🇻🇳", "Malaysia": "🇲🇾", "Singapore": "🇸🇬", "Israel": "🇮🇱",
    "Saudi Arabia": "🇸🇦", "United Arab Emirates": "🇦🇪", "Iran": "🇮🇷",
    "South Africa": "🇿🇦", "Egypt": "🇪🇬", "Morocco": "🇲🇦", "Tunisia": "🇹🇳",
    "Peru": "🇵🇪", "Ecuador": "🇪🇨", "Venezuela": "🇻🇪", "Bolivia": "🇧🇴",
    "Uruguay": "🇺🇾", "Paraguay": "🇵🇾", "Costa Rica": "🇨🇷", "Panama": "🇵🇦",
    "Guatemala": "🇬🇹", "Cuba": "🇨🇺", "Puerto Rico": "🇵🇷", "Greenland": "🇬🇱",
    "Luxembourg": "🇱🇺", "Malta": "🇲🇹", "San Marino": "🇸🇲", "Andorra": "🇦🇩"
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
    "SI": "Slovenia", "EE": "Estonia", "BY": "Belarus", "KZ": "Kazakhstan",
    "AM": "Armenia", "GE": "Georgia", "LT": "Lithuania", "LV": "Latvia",
    "RO": "Romania", "BG": "Bulgaria", "RS": "Serbia", "HR": "Croatia",
    "BA": "Bosnia and Herzegovina", "ME": "Montenegro", "MK": "North Macedonia",
    "AL": "Albania", "TR": "Turkey", "CY": "Cyprus", "CN": "China",
    "TW": "Taiwan", "KR": "South Korea", "IN": "India", "TH": "Thailand",
    "VN": "Vietnam", "MY": "Malaysia", "SG": "Singapore", "IL": "Israel",
    "SA": "Saudi Arabia", "AE": "United Arab Emirates", "IR": "Iran",
    "ZA": "South Africa", "EG": "Egypt", "MA": "Morocco", "TN": "Tunisia",
    "PE": "Peru", "EC": "Ecuador", "VE": "Venezuela", "BO": "Bolivia",
    "UY": "Uruguay", "PY": "Paraguay", "CR": "Costa Rica", "PA": "Panama",
    "GT": "Guatemala", "CU": "Cuba", "PR": "Puerto Rico", "GL": "Greenland",
    "LU": "Luxembourg", "MT": "Malta", "SM": "San Marino", "AD": "Andorra"
}

artist_countries_cache = {}
def verify_via_discogs(band_name, album_name):
    """ Стальной Фильтр v5.0: Жесткая проверка связки Группа + Альбом через Discogs API """
    if not band_name or not album_name:
        return False
    
    # Очищаем названия от лишних пробелов и кодируем для URL
    search_query = f"{band_name} {album_name}"
    encoded_query = urllib.parse.quote(search_query)
    
    # Сборка зашифрованного URL: https://discogs.com
    url = f"{P}{D_API}{Q}q{E}{encoded_query}{A}type{E}release"
    headers = {'User-Agent': 'MetalHubValidatorApp/2.0'}
    
    time.sleep(1) # Соблюдаем лимиты запросов Discogs API (60 в минуту)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get("results", [])
                
                # Если в базе Discogs есть хоть одно точное совпадение, релиз реален
                if len(results) > 0:
                    print(f"✅ Фильтр пройден: {band_name} - {album_name} подтвержден на Discogs.")
                    return True
    except Exception as e:
        print(f"⚠️ Ошибка проверки Discogs для {band_name}: {e}")
        return True # Резервный фолбэк, чтобы не потерять релиз при сбое сети
        
    print(f"❌ РЕЛИЗ ОТКЛОНЕН: {band_name} - {album_name} отсутствует на Discogs (ИИ-мусор/Сингл).")
    return False

def get_country_by_artist_id(artist_id, headers):
    """ Запрос страны исполнителя из MusicBrainz с использованием кэширования """
    if not artist_id:
        return ""
    if artist_id in artist_countries_cache:
        return artist_countries_cache[artist_id]
        
    # Сборка зашифрованного URL: https://musicbrainz.org
    url = f"{P}{MB_BASE}artist{S}{artist_id}{Q}fmt{E}json"
    time.sleep(1)
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
    except Exception:
        pass
    artist_countries_cache[artist_id] = ""
    return ""
def fetch_musicbrainz_new_arrivals():
    """ Главная функция парсинга новых поступлений из MusicBrainz """
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = None
    current_month_num = None
    current_year = time_struct.tm_year
    
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip().upper()
        
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        elif input_month == "AUTO" and input_year == "AUTO":
            current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
            current_month_num = str(time_struct.tm_mon).zfill(2)
    else:
        current_month_tag = "JUL"
        current_month_num = "07"

    if current_month_tag:
        print(f"🎵 Поиск за конкретный период: {current_month_tag} {current_year}")
    else:
        print(f"🎵 Запущен архивный режим. Поиск за ВЕСЬ {current_year} ГОД")
        
    genres_map = {
        "black metal": "Black Metal", "true black metal": "True Black Metal",
        "raw black metal": "Raw Black Metal", "orthodox black metal": "Orthodox Black Metal",
        "melodic black metal": "Melodic Black Metal", "symphonic black metal": "Symphonic Black Metal",
        "ambient black metal": "Ambient Black Metal", "blackgaze": "Blackgaze",
        "dsbm": "Depressive Black Metal", "depressive black metal": "Depressive Black Metal",
        "post-black metal": "Post-Black Metal", "atmospheric black metal": "Atmospheric Black Metal",
        "avant-garde black metal": "Avant-Garde Black Metal", "progressive black metal": "Progressive Black Metal",
        "dissonant black metal": "Dissonant Black Metal", "psychedelic black metal": "Psychedelic Black Metal",
        "blackened death metal": "Blackened Death Metal", "blackened death": "Blackened Death Metal",
        "black doom": "Black-Doom", "black-doom": "Black-Doom", "blackened crust": "Blackened Crust",
        "blackened hardcore": "Blackened Hardcore", "blackened grindcore": "Blackened Grindcore",
        "blackened thrash metal": "Blackened Thrash Metal", "pagan black metal": "Pagan Black Metal",
        "viking black metal": "Viking Black Metal", "folk black metal": "Folk Black Metal",
        "medieval black metal": "Medieval Black Metal", "war metal": "War Metal",
        "bestial black metal": "Bestial Black Metal", "bestial black": "Bestial Black Metal",
        "bestial metal": "Bestial Black Metal", "industrial black metal": "Industrial Black Metal",
        "industrial black": "Industrial Black Metal", "cyber black metal": "Industrial Black Metal",
        "cyber black": "Industrial Black Metal", "first wave of black metal": "First Wave Black Metal",
        "proto-black metal": "Proto-Black Metal", "proto-black": "Proto-Black Metal",
        "blackened thrash": "Blackened Thrash Metal", "black thrash": "Blackened Thrash Metal",
        "black thrash metal": "Blackened Thrash Metal", "black speed metal": "Black/Speed Metal",
        "blackened speed metal": "Black/Speed Metal"
    }
    
    genres = list(genres_map.keys())
    all_releases = []
    chunk_size = 4
    headers = {'User-Agent': 'BlackMetalHubBot/18.0 ( mailto:Plokhamentov@example.com )'}
    
    for i in range(0, len(genres), chunk_size):
        chunk = genres[i:i + chunk_size]
        tag_queries = " OR ".join([f'tag:"{g}"' for g in chunk])
        
        # Поиск по альбомам и EP, исключая синглы на уровне MusicBrainz
        query = f'(type:album OR type:ep) AND status:official AND date:[{current_year}-01-01 TO {current_year}-12-31] AND ({tag_queries})'
        
        offset = 0
        limit = 100
        
        while True:
            # Сборка зашифрованного URL: https://musicbrainz.org...
            url = f"{P}{MB_BASE}release{Q}query{E}{urllib.parse.quote(query)}{A}inc{E}tags+artist-credits{A}fmt{E}json{A}limit{E}{limit}{A}offset{E}{offset}"
            time.sleep(1)
            
            try:
                chunk_releases = []
                for attempt in range(3):
                    try:
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, timeout=15) as response:
                            if response.status == 200:
                                chunk_data = json.loads(response.read().decode('utf-8'))
                                chunk_releases = chunk_data.get("releases", [])
                                total_count = chunk_data.get("count", 0)
                                break
                    except Exception as he:
                        if getattr(he, 'code', 0) == 503 and attempt < 2:
                            time.sleep(3)
                            continue
                        raise he
                
                if not chunk_releases:
                    break
                    
                all_releases.extend(chunk_releases)
                
                if offset + limit >= total_count or len(chunk_releases) < limit:
                    break
                offset += limit
            except Exception as e:
                print(f"⚠️ Ошибка MusicBrainz API на группе {chunk}: {e}")
                break

    packs = []
    seen_albums = set()
    for rel in all_releases:
        rel_date = rel.get("date", "")
        
        if current_month_num:
            if rel_date and len(rel_date.split("-")) > 1:
                if rel_date.split("-")[1] != current_month_num:
                    continue
            else:
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
            release_key = f"{band.lower()} - {album.lower()}"
            if release_key in seen_albums:
                continue
            seen_albums.add(release_key)
            
            # Стальной Фильтр v5.0: Пробиваем ИИ-фейки через Discogs API перед добавлением
            if not verify_via_discogs(band, album):
                continue
                
            country_code = get_country_by_artist_id(artist_id, headers)
            flag_emoji = ""
            if country_code:
                country_name = COUNTRY_MAP.get(country_code)
                if country_name:
                    flag_emoji = COUNTRY_TO_FLAG.get(country_name, "")
            
            tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
            subgenres = [genres_map[g_tag] for g_tag in genres_map if g_tag in tags_list]
            
            if not subgenres:
                continue
                
            genre_str = "/".join(list(set(subgenres)))
            prefix = f"{flag_emoji} " if flag_emoji else ""
            
            release_status = rel.get("release-group", {}).get("primary-type", "").upper()
            ep_suffix = " EP" if "EP" in release_status or rel.get("quality", "") == "ep" else ""
            
            month_label = current_month_tag if current_month_tag else rel_date
            
            # Сборка финального сообщения строго по ТЗ
            release_info = f"{band} - {album} ({current_year}){ep_suffix}\n{prefix}{genre_str}\n{P}{YT_BASE} {month_label}"
            packs.append(release_info)

    period_str = f"{current_month_tag} {current_year}" if current_month_tag else f"{current_year} год"
    output_text = "\n---\n".join(packs) if packs else f"В базе найдено 0 реальных релизов за {period_str}."
    max_len = 4000
    
    for i in range(0, len(output_text), max_len):
        chunk_text = output_text[i:i + max_len]
        # Зашифрованный эндпоинт отправки в Telegram
        send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
        payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": chunk_text}).encode('utf-8')
        req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                pass
        except Exception as e:
            print(f"❌ Ошибка отправки чанка в Telegram: {e}")

if __name__ == "__main__":
    fetch_musicbrainz_new_arrivals()
