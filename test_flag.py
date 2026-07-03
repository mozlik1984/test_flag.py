import urllib.request
import urllib.parse
import json
import time
import sys
import re

BOT_TOKEN = "8615944325:AAFzRUmPbUzGtmBHUy4F4gp_gLd3dFBHAd0"
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58); P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵"
}

def fetch_musicbrainz_new_arrivals():
    # 1. АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ ТЕКУЩЕЙ ДАТЫ
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    
    # 2. ПЕРЕХВАТ РУЧНОГО ВВОДА С ЭКРАНА GITHUB
    # Проверяем, передал ли нам Гитхаб параметры из текстовых полей
    if len(sys.argv) > 2:
        input_month = sys.argv[1].strip().upper()
        input_year = sys.argv[2].strip()
        
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print(f"🚀 Запуск поиска релизов по цели: {current_month_tag} {current_year} (Числовой месяц: {current_month_num})")
    
    # 3. ЛЕГАЛЬНЫЙ ЗАПРОС К API MUSICBRAINZ
    query = f'type:album AND status:official AND date:{current_year}-{current_month_num} AND tag:"black metal"'
    url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&fmt=json&limit=30"
    
    headers = {
        'User-Agent': 'BlackMetalHubBot/10.0 ( mailto:Plokhomentov@example.com )'
    }
    
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
                    band = artist_credit[0].get("artist", {}).get("name", "").strip()
                    album = rel.get("title", "").strip()
                    
                    if band and album:
                        release_key = f"{band} - {album}".lower()
                        if release_key in seen_albums:
                            continue
                        seen_albums.add(release_key)
                        
                        country_info = rel.get("country", "")
                        if country_info == "NO": country_info = "Norway"
                        if country_info == "SE": country_info = "Sweden"
                        if country_info == "FI": country_info = "Finland"
                        if country_info == "DE": country_info = "Germany"
                        if country_info == "FR": country_info = "France"
                        if country_info == "US": country_info = "United States"
                        if country_info == "GB": country_info = "United Kingdom"
                        
                        flag = COUNTRY_TO_FLAG.get(country_info, "🇳🇴")
                        
                        # Собираем строчку импорта
                        block = f"{band} - {album} ({current_year})\n{flag} Black Metal\nhttps://youtube.com {current_month_tag}"
                        packs.append(block)
                        
                if packs:
                    return "\n---\n".join(packs)
                    
        return f"🌑 Проверенных полноформатных новинок в базе за {current_month_tag} {current_year} на этой неделе пока не зафиксировано."
        
    except Exception as e:
        return f"❌ Ошибка агрегатора MusicBrainz API: {str(e)}"

def send_to_admin(content_text, month_tag, year_val):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ УЛОВ МАШИНЫ ВРЕМЕНИ ЗА {month_tag} {year_val} ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Просто нажми на блок выше — текст скопируется. Вставь его мне в чат! Ютуб-превью отключено автоматически.</i>"
    
    data = urllib.parse.urlencode({
        'chat_id': ADMIN_CHAT_ID, 
        'text': formatted_msg, 
        'parse_mode': 'HTML', 
        'disable_web_page_preview': 'true'
    }).encode('utf-8')
    
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    final_report = fetch_musicbrainz_new_arrivals()
    
    # Вытаскиваем теги для красивого заголовка отчета в ТГ
    m_tag = "JUL"
    y_val = time.gmtime().tm_year
    if len(sys.argv) > 2 and sys.argv[1].strip().upper() != "AUTO":
        m_tag = sys.argv[1].strip().upper()
    if len(sys.argv) > 2 and sys.argv[2].strip() != "AUTO":
        y_val = sys.argv[2].strip()
        
    send_to_admin(final_report, m_tag, y_val)
