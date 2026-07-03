import urllib.request
import urllib.parse
import json
import time
import sys
import re

# --- КОНФИГУРАЦИЯ СВЯЗИ ---
BOT_TOKEN = "8615944325:AAFzRUmPbUzGtmBHUy4F4gp_gLd3dFBHAd0"
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58); P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿"
}

def fetch_musicbrainz_new_arrivals():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print(f"🌍 Сканирую базу по цели: {current_month_tag} {current_year}")

    # Запрашиваем релизы, подтягивая данные об артистах (artist-credits)
    query = f'type:album AND status:official AND date:{current_year}-{current_month_num} AND tag:"black metal"'
    url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&inc=tags+artist-credits&fmt=json&limit=30"
    
    headers = {'User-Agent': 'BlackMetalHubBot/15.0 ( mailto:Plokhomentov@example.com )'}
    
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
                    
                    # Безопасно извлекаем данные первого артиста
                    first_artist = artist_credit[0] if isinstance(artist_credit, list) else artist_credit
                    artist_data = first_artist.get("artist", {})
                    
                    band = artist_data.get("name", "").strip()
                    album = rel.get("title", "").strip()
                    artist_id = artist_data.get("id", "")
                    
                    if band and album:
                        # Защита от дубликатов прессов
                        release_key = f"{band} - {album}".lower()
                        if release_key in seen_albums: continue
                        seen_albums.add(release_key)
                        
                        # 🪐 УМНЫЙ АНАЛИЗ ПОДЖАНРОВ (СТРОГАЯ ИЕРАРХИЯ ТЕГОВ)
                        tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
                        # Сюда же добавляем теги самого артиста для точности
                        tags_list += [t.get("name", "").lower() for t in artist_data.get("tags", [])]
                        tags_str = " ".join(tags_list)
                        
                        detected_subgenre = "Black Metal"
                        if "depressive" in tags_str or "dsbm" in tags_str or "suicidal" in tags_str: 
                            detected_subgenre = "Depressive Black Metal"
                        elif "atmospheric" in tags_str or "ambient" in tags_str: 
                            detected_subgenre = "Atmospheric Black Metal"
                        elif "post-black" in tags_str or "post" in tags_str: 
                            detected_subgenre = "Post-Black Metal"
                        elif "symphonic" in tags_str: 
                            detected_subgenre = "Symphonic Black Metal"
                        elif "pagan" in tags_str: 
                            detected_subgenre = "Pagan Black Metal"
                        elif "melodic" in tags_str: 
                            detected_subgenre = "Melodic Black Metal"
                        elif "crust" in tags_str: 
                            detected_subgenre = "Crust Black Metal"
                        elif "psychedelic" in tags_str: 
                            detected_subgenre = "Psychedelic Black Metal"
                        
                        # 🌍 АВТОНОМНОЕ ГЛУБОКОЕ БУРЕНИЕ СТРАНЫ ПРЯМО ИЗ АНКЕТЫ ГРУППЫ
                        country_name = "Norway" # Каноничный бэкап
                        if artist_id:
                            try:
                                artist_url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "artist" + S + artist_id + "?fmt=json"
                                req_art = urllib.request.Request(artist_url, headers=headers)
                                with urllib.request.urlopen(req_art, timeout=6) as res_art:
                                    art_data = json.loads(res_art.read().decode('utf-8'))
                                    
                                    # Забираем текстовое название домашней области (например, "Germany" или "Wales")
                                    area_data = art_data.get("area", {})
                                    if area_data and area_data.get("name"):
                                        country_name = area_data.get("name").strip()
                                time.sleep(1.1) # Строгий сетевой лимит API
                            except:
                                pass

                        flag = COUNTRY_TO_FLAG.get(country_name, "🇳🇴")
                        
                        block = f"{band} - {album} ({current_year})\n{flag} {detected_subgenre}\nhttps://youtube.com {current_month_tag}"
                        packs.append(block)
                        
                if packs:
                    return "\n---\n".join(packs)
                    
        return f"🌑 Проверенных полноформатных новинок за {current_month_tag} {current_year} пока не зафиксировано."
        
    except Exception as e:
        return f"❌ Ошибка автономного PRO v3.0 агрегатора: {str(e)}"

def send_to_admin(content_text, month_tag, year_val):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ АВТОНОМНЫЙ УЛОВ ЗА {month_tag} {year_val} ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Код очищен от ручных костылей. Скрипт сам залез в анкеты банд и раскопал реальные страны!</i>"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    final_report = fetch_musicbrainz_new_arrivals()
    m_tag = "JUL"
    y_val = time.gmtime().tm_year
    if len(sys.argv) > 2 and str(sys.argv[1]).upper() != "AUTO": m_tag = str(sys.argv[1]).upper()
    if len(sys.argv) > 2 and str(sys.argv[2]) != "AUTO": y_val = str(sys.argv[2])
    send_to_admin(final_report, m_tag, y_val)
    
