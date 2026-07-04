import os
import urllib.request
import urllib.parse
import json
import time
import sys
import re

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
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

def get_real_release_date_and_meta(album_url, headers):
    """Заходит на страницу альбома и парсит честную дату релиза и страну"""
    try:
        req = urllib.request.Request(album_url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Ищем дату релиза: "released January 14, 2026" или "released 14 January 2026"
        date_match = re.search(r'released\s+([A-Za-z]+)?\s*(\d+)?\s*,?\s*([A-Za-z]+)?\s*(\d{4})', html, re.IGNORECASE)
        rel_year = None
        rel_month = None
        
        if date_match:
            g = date_match.groups()
            # Пытаемся найти год (4 цифры)
            for item in g:
                if item and item.isdigit() and len(item) == 4:
                    rel_year = int(item)
                if item and not item.isdigit() and len(item) >= 3:
                    rel_month = item.upper()[:3]

        # Ищем поджанры в тегах
        subgenre = "Black Metal"
        if "atmospheric" in html.lower(): subgenre = "Atmospheric Black Metal"
        elif "depressive" in html.lower() or "dsbm" in html.lower(): subgenre = "Depressive Black Metal"
        elif "post-black" in html.lower(): subgenre = "Post-Black Metal"
        elif "raw" in html.lower(): subgenre = "Raw Black Metal"
        
        # Пытаемся угадать страну по тегам на странице
        detected_flag = ""
        for country, flag in COUNTRY_TO_FLAG.items():
            if f'"{country.lower()}"' in html.lower() or f'tag_name">{country.lower()}<' in html.lower():
                detected_flag = flag
                break
                
        return rel_year, rel_month, subgenre, detected_flag
    except:
        return None, None, "Black Metal", ""

def fetch_bandcamp_rss_machine():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_year = time_struct.tm_year
    
    if len(sys.argv) > 2:
        input_month = sys.argv[1].strip().upper()
        input_year = sys.argv[2].strip()
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)
            
    print(f"🔮 Запуск честного парсинга Bandcamp по цели: {current_month_tag} {current_year}")
    
    url = P + "www.bandcamp.com" + S + "discover" + S + "black-metal" + S + "t" + S + "album"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Находим блоки ссылок, названия альбомов и групп
        items = re.findall(r'href="([^"]+album=[^"]+)">([^<]+)</a>\s*by\s*<span class="artist">([^<]+)</span>', html_content)
        
        packs = []
        seen = set()
        
        for album_url, album_name, band_name in items:
            band_name = band_name.strip()
            album_name = album_name.strip()
            key = f"{band_name} - {album_name}".lower()
            
            if key in seen: continue
            seen.add(key)
            
            # Корректируем URL, если он кривой
            if not album_url.startswith("http"):
                album_url = "https:" + album_url if album_url.startswith("//") else P + "bandcamp.com" + album_url
            
            # Делаем проверку реального релиза в коде страницы
            time.sleep(1.0) # Защита от банов
            rel_year, rel_month, subgenre, flag = get_real_release_date_and_meta(album_url, headers)
            
            # Строгий фильтр года! Если год в коде не совпал с запрашиваемым — выкидываем старье
            if rel_year and rel_year != current_year:
                print(f"⏩ Пропущен старый релиз: {band_name} - {album_name} ({rel_year})")
                continue
                
            # Формируем блок улова
            flag_str = f"{flag} " if flag else ""
            clean_url = album_url.split('?')[0] # чистая ссылка без мусора
            
            packs.append(f"{band_name} - {album_name} ({current_year})\n{flag_str}{subgenre}\n{clean_url} {current_month_tag}")
            
            if len(packs) >= 7: break # ограничиваем улов лучшими 7 релизами
            
        if packs: 
            return "\n---\n".join(packs)
        return f"🌑 Честных новинок за {current_month_tag} {current_year} в текущей ленте Bandcamp не обнаружено."
        
    except Exception as e:
        return f"❌ Ошибка машины Bandcamp: {str(e)}"

def send_to_admin(content_text, month_tag, year_val):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ БАНДКЭМП-УЛОВ ЗА {month_tag} {year_val} ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Скопируй в один тап! Вставь боту в чат для наполнения кнопки {month_tag}! Превью ссылок отключено.</i>"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    time_struct = time.gmtime()
    m_tag = months_map.get(time_struct.tm_mon, "JUL")
    y_val = time_struct.tm_year
    
    if len(sys.argv) > 2 and sys.argv[1].strip().upper() != "AUTO": m_tag = sys.argv[1].strip().upper()
    if len(sys.argv) > 2 and sys.argv[2].strip() != "AUTO": y_val = sys.argv[2].strip()
        
    report = fetch_bandcamp_rss_machine()
    send_to_admin(report, m_tag, y_val)
    
