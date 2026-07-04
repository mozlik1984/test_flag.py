import os
import urllib.request
import urllib.parse
import json
import time
import sys
import re

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Ваша фирменная склейка для защиты ссылок от скрытия на телефоне
S = chr(47); C = chr(58); Q = chr(63); E = chr(61); A = chr(38)
P = "https" + C + S + S + "www."

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵"
}

def get_real_release_date_and_meta(album_url, headers):
    try:
        req = urllib.request.Request(album_url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        date_match = re.search(r'released\s+([A-Za-z]+)?\s*(\d+)?\s*,?\s*([A-Za-z]+)?\s*(\d{4})', html, re.IGNORECASE)
        rel_year = None
        rel_month = None
        
        if date_match:
            g = date_match.groups()
            for item in g:
                if item and item.isdigit() and len(item) == 4:
                    rel_year = int(item)
                if item and not item.isdigit() and len(item) >= 3:
                    rel_month = item.upper()[:3]

        subgenre = "Black Metal"
        if "atmospheric" in html.lower(): subgenre = "Atmospheric Black Metal"
        elif "depressive" in html.lower() or "dsbm" in html.lower(): subgenre = "Depressive Black Metal"
        elif "post-black" in html.lower(): subgenre = "Post-Black Metal"
        elif "raw" in html.lower(): subgenre = "Raw Black Metal"
        
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
    
    # Исправленное чтение аргументов
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)
            
    print(f"🔮 Машина времени Bandcamp активирована: поиск {current_month_tag} {current_year}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    packs = []
    seen = set()
    
    # Листаем глубже, если затребован архивный месяц/год
    max_pages = 8 if current_year < time_struct.tm_year or current_month_tag != months_map.get(time_struct.tm_mon) else 2
    
    try:
        for page in range(1, max_pages + 1):
            print(f"🔎 Сканируем страницу {page}...")
            # Безопасная сборка URL для парсинга через переменные
            url = P + "bandcamp.com" + S + "tag" + S + "black-metal" + Q + "tab" + E + "all_releases" + A + "page" + E + str(page)
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
            items = re.findall(r'href="([^"]+album=[^"]+?)"[^>]*>.*?<div class="title">([^<]+)</div>.*?<div class="artist">([^<]+)</div>', html_content, re.DOTALL)
            
            if not items:
                items = re.findall(r'href="([^"]+album=[^"]+)">([^<]+)</a>\s*by\s*<span class="artist">([^<]+)</span>', html_content)
                
            if not items: break
            
            for album_url, album_name, band_name in items:
                band_name = band_name.strip()
                album_name = album_name.strip()
                key = f"{band_name} - {album_name}".lower()
                
                if key in seen: continue
                seen.add(key)
                
                # Принудительно чистим ссылки и добавляем www через склейку
                if "bandcamp.com" in album_url:
                    # Выдергиваем поддомен группы (например, https://bandcamp.com)
                    subdomain_match = re.search(r'https?://([^/]+)', album_url)
                    if subdomain_match:
                        subdomain = subdomain_match.group(1)
                        if not subdomain.startswith("www.") and subdomain.count('.') == 1:
                            subdomain = "www." + subdomain
                        album_path = album_url.split("bandcamp.com")[-1].split('?')[0]
                        final_link = "https" + C + S + S + subdomain + album_path
                    else:
                        final_link = album_url.split('?')[0]
                else:
                    final_link = P + "bandcamp.com" + album_url.split('?')[0]
                
                time.sleep(0.8)
                rel_year, rel_month, subgenre, flag = get_real_release_date_and_meta(final_link, headers)
                
                if rel_year and rel_year != current_year:
                    continue
                if rel_month and rel_month != current_month_tag:
                    continue
                    
                flag_str = f"{flag} " if flag else ""
                
                packs.append(f"{band_name} - {album_name} ({current_year})\n{flag_str}{subgenre}\n{final_link} {current_month_tag}")
                
                if len(packs) >= 7: break
            if len(packs) >= 7: break
            
        if packs: 
            return "\n---\n".join(packs)
        return f"🌑 Честных новинок за {current_month_tag} {current_year} в архивах ленты Bandcamp не обнаружено."
        
    except Exception as e:
        return f"❌ Ошибка машины Bandcamp: {str(e)}"

def send_to_admin(content_text, month_tag, year_val):
    api_url = "https" + C + S + S + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ БАНДКЭМП-УЛОВ ЗА {month_tag} {year_val} ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Скопируй в один тап! Вставь боту в чат для наполнения кнопки {month_tag}! Превью ссылок отключено.</i>"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    time_struct = time.gmtime()
    m_tag = months_map.get(time_struct.tm_mon, "JUL")
    y_val = time_struct.tm_year
    
    if len(sys.argv) > 2:
        if str(sys.argv[1]).strip().upper() != "AUTO": m_tag = str(sys.argv[1]).strip().upper()
        if str(sys.argv[2]).strip() != "AUTO": y_val = str(sys.argv[2]).strip()
        
    report = fetch_bandcamp_rss_machine()
    send_to_admin(report, m_tag, y_val)
    
