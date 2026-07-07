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

# Маппинг ISO кодов в полные названия
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

# Локальный оперативный кэш для стран
artist_countries_cache = {}

def get_country_by_artist_id(artist_id, headers):
    if not artist_id:
        return ""
    if artist_id in artist_countries_cache:
        return artist_countries_cache[artist_id]
        
    url = f"{P}musicbrainz.org{S}ws{S}2{S}artist{S}{artist_id}?fmt=json"
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
                    country_code = codes if codes else ""
                
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
    current_month_tag = None  # По умолчанию None для поиска за весь год
    current_month_num = None
    current_year = time_struct.tm_year
    
    # Умный разбор аргументов, заточенный под GitHub Actions (AUTO / конкретные значения)
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip().upper()
        
        # 1. Разбираемся с годом
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)
            
        # 2. Разбираемся с месяцем
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        else:
            # Если месяц оставлен как AUTO, сбрасываем его в None, 
            # чтобы включился архивный режим поиска за ВЕСЬ ГОД
            current_month_tag = None
            current_month_num = None

    # Выводим инфо для логов GitHub
    if current_month_tag:
        print(f"🛰️ Поиск за конкретный период: {current_month_tag} {current_year}")
    else:
        print(f"🛰️ Запущен архивный режим. Поиск за ВЕСЬ {current_year} ГОД")

    # Сетка поджанров, усиленная War и Industrial направлениями
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
        "cyber black": "Industrial Black Metal"
    }
    
    genres = list(genres_map.keys())
    all_releases = []
    chunk_size = 4
    headers = {'User-Agent': 'BlackMetalHubBot/17.0 ( mailto:Plokhomentov@example.com )'}
    
    # Сбор релизов пачками
    for i in range(0, len(genres), chunk_size):
        chunk = genres[i:i + chunk_size]
        tag_queries = " OR ".join([f'tag:"{g}"' for g in chunk])
                        # ИСПРАВЛЕНО: Правильный синтаксис Lucene для поиска за весь год целиком
        query = f'type:album AND status:official AND date:[{current_year}-01-01 TO {current_year}-12-31] AND ({tag_queries})'
        
        offset = 0
        limit = 100
        
        # Цикл пагинации для выкачивания абсолютно всех страниц ответов
        while True:
            url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + f"&inc=tags+artist-credits&fmt=json&limit={limit}&offset={offset}"
            time.sleep(1)
            
            try:
                chunk_releases = []
                total_count = 0
                for attempt in range(3):
                    try:
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, timeout=15) as response:
                            if response.status == 200:
                                chunk_data = json.loads(response.read().decode('utf-8'))
                                chunk_releases = chunk_data.get("releases", [])
                                total_count = chunk_data.get("count", 0)
                                break
                    except urllib.error.HTTPError as he:
                        if he.code == 503 and attempt < 2:
                            time.sleep(3)
                            continue
                        raise he
                
                if not chunk_releases:
                    break
                    
                all_releases.extend(chunk_releases)
                
                # Если дошли до конца выдачи, выходим на следующую группу жанров
                if offset + limit >= total_count or len(chunk_releases) < limit:
                    break
                    
                offset += limit
                print(f"   -> Загружено {len(all_releases)} релизов из текущей группы жанров...")
                
            except Exception as e:
                print(f"⚠️ Ошибка на группе {chunk} (offset {offset}): {e}")
                break

    packs = []
    seen_albums = set()
    
    # Фильтрация и форматирование данных
    for rel in all_releases:
        rel_date = rel.get("date", "")
        
        # Фильтрация по месяцу активна ТОЛЬКО если передан аргумент месяца
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
            release_key = band.lower() + " - " + album.lower()
            if release_key in seen_albums: 
                continue
            seen_albums.add(release_key)
            
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
            
            # Подставляем метку месяца (если ищем за месяц), либо полную дату релиза (если ищем за год)
            month_label = current_month_tag if current_month_tag else rel_date
            
            release_info = f"{band} - {album} ({current_year})\n{prefix}{genre_str}\nhttps://youtube.com {month_label}"
            packs.append(release_info)

    # Итоговая отправка в Telegram
    period_str = f"{current_month_tag} {current_year}" if current_month_tag else f"{current_year} год"
    output_text = f"\n---\n".join(packs) if packs else f"🤷 За {period_str} релизов не найдено."
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
