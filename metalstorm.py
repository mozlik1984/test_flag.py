import os
import urllib.request
import urllib.parse
import json
import time
import sys
import re

# Настройки бота и администратора
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# ASCII-шифрование эндпоинтов Metal Storm и Telegram
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
A = chr(38)  # &
E = chr(61)  # =
P = "https" + C + S + S

# Базовые скрытые домены и пути
MS_BASE = "metalstorm.net" + S
MS_REL_PATH = "events" + S + "releases.php"
MS_BAND_PATH = "bands" + S + "band.php"
TG_BASE = "api.telegram.org" + S + "bot"
YT_BASE = "youtube.com"

# Расширенный список эмодзи флагов для Metal Storm (80 стран)
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
    "Luxembourg": "🇱🇺", "Malta": "🇲🇹", "San Marino": "🇸微", "Andorra": "🇦🇩"
}

band_countries_cache = {}
def fetch_metalstorm_releases():
    """ Основная функция сбора и фильтрации релизов с Metal Storm """
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    
    time_struct = time.gmtime()
    current_year = time_struct.tm_year
    current_month_num = time_struct.tm_mon
    
    # Работа по требованию через аргументы запуска GitHub Actions
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip().upper()
        
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_num = months_num_map[input_month]
            
    current_month_tag = months_map.get(current_month_num, "JUL")
    print(f"🎵 Metal Storm парсер запущен за период: {current_month_tag} {current_year}")
    
    # Сборка зашифрованного URL архива релизов: https://metalstorm.net
    url = f"{P}{MS_BASE}events{S}releases.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    html_content = ""
    try:
        req = urllib.request.Request(url, headers=headers)
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
    
    # Поиск таблицы релизов в HTML коде через строковые маркеры
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
