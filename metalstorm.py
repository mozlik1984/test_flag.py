import os
import urllib.request
import urllib.parse
import json
import time
import sys

# Настройки бота и администратора
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Тотальное ASCII-шифрование всех ссылок и путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
A = chr(38)  # &
E = chr(61)  # =
P = "https" + C + S + S

# Скрытые домены и эндпоинты
MB_BASE = "musicbrainz.org" + S + "ws" + S + "2" + S
MA_BASE = "://metal-archives.com" + S + "search" + S + "ajax-band-search" + S
TG_BASE = "api.telegram.org" + S + "bot"
YT_BASE = "youtube.com"
MS_BASE = "metalstorm.net" + S

# Полный маскировочный набор заголовков под реальный браузер (Анти-403)
REAL_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Расширенный список эмодзи флагов (80 стран)
COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "China": "🇨🇳", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰",
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
def verify_via_metal_archives(band_name):
    """ Проверка группы на вшивость через защищенный API-эндпоинт Metal Archives """
    if not band_name:
        return False
    encoded_band = urllib.parse.quote(band_name)
    url = f"{P}{MA_BASE}{Q}field{E}name{A}query{E}{encoded_band}"
    try:
        req = urllib.request.Request(url, headers=REAL_HEADERS)
        with urllib.request.urlopen(req, timeout=7) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("iTotalRecords", 0) > 0:
                    return True
    except Exception:
        return True
    return False

def get_country_by_artist_id(artist_id, headers):
    """ Запрос страны исполнителя с использованием кэширования """
    if not artist_id:
        return ""
    if artist_id in artist_countries_cache:
        return artist_countries_cache[artist_id]
        
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
                    country_code = codes if codes else ""
                
                artist_countries_cache[artist_id] = str(country_code).upper()
                return artist_countries_cache[artist_id]
    except Exception:
        pass
    artist_countries_cache[artist_id] = ""
    return ""

def fetch_metalstorm_releases():
    """ Главная функция парсинга новых поступлений с маскировкой под мобильный браузер """
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    
    time_struct = time.gmtime()
    current_year = time_struct.tm_year
    current_month_num = time_struct.tm_mon
    
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip().upper()
        
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_num = months_num_map[input_month]
            
    current_month_tag = months_map.get(current_month_num, "JUL")
    print(f"🎵 Metal Storm парсер запущен за период: {current_month_tag} {current_year}")
    
    url = f"{P}{MS_BASE}events{S}releases.php"
    
    html_content = ""
    try:
        # Передаем обновленный словарь REAL_HEADERS вместо старых настроек
        req = urllib.request.Request(url, headers=REAL_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                html_content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"❌ Критическая ошибка подключения к Metal Storm: {e}")
        return

    if not html_content:
        print("❌ Не удалось получить данные: пустая страница.")
        return

    packs = []
    seen_releases = set()
    
    table_start = html_content.find('<table')
    if table_start == -1:
        print("❌ Таблица релизов не найдена в HTML коде.")
        return
    # Построчный скрейпинг таблицы без тяжелых внешних библиотек
    pos = table_start
    while True:
        tr_start = html_content.find('<tr', pos)
        if tr_start == -1:
            break
        tr_end = html_content.find('</tr>', tr_start)
        if tr_end == -1:
            break
        
        row_html = html_content[tr_start:tr_end]
        pos = tr_end + 5
        
        # Фильтруем строки, пропускаем шапки таблиц
        if 'class="header"' in row_html or '<th>' in row_html:
            continue
            
        # Извлекаем ячейки <td>
        tds = []
        td_pos = 0
        while True:
            td_s = row_html.find('<td', td_pos)
            if td_s == -1:
                break
            td_e = row_html.find('</td>', td_s)
            if td_e == -1:
                break
            tds.append(row_html[td_s:td_e])
            td_pos = td_e + 5
            
        if len(tds) < 4:
            continue
            
        # Грубый поиск данных в ячейках через текстовые маркеры
        band_raw = tds[0]
        album_raw = tds[1]
        genre_raw = tds[2].lower()
        date_raw = tds[3]
        
        # Проверяем, относится ли релиз к блэк-металу
        is_black = False
        detected_genres = []
        for g_key, g_val in GENRES_MAP.items():
            if g_key in genre_raw:
                is_black = True
                if g_val not in detected_genres:
                    detected_genres.append(g_val)
                    
        if not is_black:
            continue
            
        # Очистка названия группы и альбома от HTML-тегов
        def clean_html(text):
            while True:
                s_idx = text.find('<')
                if s_idx == -1:
                    break
                e_idx = text.find('>', s_idx)
                if e_idx == -1:
                    break
                text = text[:s_idx] + text[e_idx+1:]
            return text.strip()
            
        band = clean_html(band_raw)
        album = clean_html(album_raw)
        genre_str = "/".join(detected_genres) if detected_genres else "Black Metal"
        
        # Извлечение страны (ищем по ссылкам на флаги или кодам)
        country_name = ""
        for c_name in COUNTRY_TO_FLAG:
            if c_name.lower() in row_html.lower():
                country_name = c_name
                break
                
        flag_emoji = COUNTRY_TO_FLAG.get(country_name, "")
        prefix = f"{flag_emoji} " if flag_emoji else ""
        
        # Проверка даты и формата (EP или Full-length)
        ep_suffix = ""
        if "[ep]" in album.lower() or " ep" in album.lower():
            ep_suffix = " EP"
            album = album.replace("[EP]", "").replace("[ep]", "").strip()
            
        # Проверка соответствия запрашиваемому месяцу и году
        # Формат даты на Metal Storm обычно: DD.MM.YYYY или MM.YYYY
        if str(current_year) not in date_raw:
            continue
            
        month_match = False
        target_month_str = f".{str(current_month_num).zfill(2)}."
        if target_month_str in date_raw or f" {current_month_tag.lower()} " in date_raw.lower():
            month_match = True
            
        if not month_match:
            continue
            
        release_key = f"{band.lower()} - {album.lower()}"
        if release_key in seen_releases:
            continue
            seen_releases.add(release_key)
        # Безопасная сборка сообщения строго по нашему шаблону ТЗ
        release_info = f"{band} - {album} ({current_year}){ep_suffix}\n{prefix}{genre_str}\n{P}{YT_BASE} {current_month_tag}"
        packs.append(release_info)

    # Формируем финальный текстовый пакет для отправки
    period_str = f"{current_month_tag} {current_year}"
    output_text = "\n---\n".join(packs) if packs else f"В базе найдено 0 реальных релизов за {period_str}."
    
    # Безопасная нарезка на чанки для обхода лимитов Telegram API
    max_len = 4000
    for i in range(0, len(output_text), max_len):
        chunk_text = output_text[i:i + max_len]
        
        # Сборка полностью скрытого эндпоинта отправки Telegram бота
        send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
        payload = json.dumps({
            "chat_id": ADMIN_CHAT_ID, 
            "text": chunk_text
        }).encode('utf-8')
        
        req = urllib.request.Request(
            send_url, 
            data=payload, 
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                pass
        except Exception as e:
            print(f"❌ Ошибка отправки чанка в Telegram: {e}")

if __name__ == "__main__":
    fetch_metalstorm_releases()
