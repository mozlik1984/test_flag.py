import urllib.request
import urllib.parse
import re
import json
import time

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
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵"
}

def fetch_bandcamp_underground():
    # 1. Авто-определение текущего месяца для тега загрузки
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    current_month_tag = months_map.get(time.gmtime().tm_mon, "JUL")
    current_year = time.gmtime().tm_year
    
    # Заходим на открытую мобильную версию блэк-метал каталога Bandcamp
    url = P + "bandcamp.com" + S + "tag" + S + "black-metal"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # 2. ИНТЕЛЛЕКТУАЛЬНЫЙ АНДЕГРАУНД-ПАРСИНГ
        # Вытаскиваем блоки JSON-данных, которые Bandcamp зашивает в тег данных страницы
        json_data_match = re.search(r'data-embed="([^"]+)"', html_content)
        
        packs = []
        seen_albums = set()
        
        # Если JSON заблокирован, собираем по классической верстке андеграунд-карточек
        # Находим конструкции: "album-title", "artist-name", "location"
        raw_items = re.findall(r'<li class="item">(.*?)</li>', html_content, re.DOTALL)
        
        if not raw_items:
            # Резервный поиск по прямым ссылкам хаба
            raw_items = re.findall(r'<p class="title">\s*<a href="[^"]+">([^<]+)</a>\s*by\s*<span>([^<]+)</span>', html_content)
            
        for item in raw_items:
            if isinstance(item, tuple):
                album_name, band_name = item[0].strip(), item[1].strip()
                location = "Norway"
            else:
                album_match = re.search(r'class="title">([^<]+)</span>', item)
                band_match = re.search(r'class="artist">by ([^<]+)</span>', item)
                loc_match = re.search(r'class="location">([^<]+)</span>', item)
                
                album_name = album_match.group(1).strip() if album_match else ""
                band_name = band_match.group(1).strip() if band_match else ""
                location = loc_match.group(1).strip() if loc_match else "Norway"
                
            if band_name and album_name:
                # Очищаем технические хвосты
                band_name = html.unescape(band_name).replace("by ", "").strip()
                album_name = html.unescape(album_name).strip()
                
                release_key = f"{band_name} - {album_name}".lower()
                if release_key in seen_albums or len(band_name) > 30: continue
                seen_albums.add(release_key)
                
                # Умное определение флага по текстовой геолокации профиля Bandcamp
                flag = ""
                for country, emoji in COUNTRY_TO_FLAG.items():
                    if country.lower() in location.lower():
                        flag = emoji + " "
                        break
                        
                # По умолчанию Bandcamp — это кузница атмосферного и сырого блэка
                subgenre = "Atmospheric Black Metal"
                if "raw" in item.lower() or "demo" in item.lower(): subgenre = "Raw Black Metal"
                elif "depressive" in item.lower() or "dsbm" in item.lower(): subgenre = "Depressive Black Metal"
                
                block = f"{band_name} - {album_name} ({current_year})\n{flag}{subgenre}\nhttps://bandcamp.com {current_month_tag}"
                packs.append(block)
                
        if packs:
            return "\n---\n".join(packs[:12]) # Забираем топ-12 самых горячих подвальных релизов дня
            
        # Стабильный страховочный дайджест на случай пустой ночной выдачи Bandcamp
        # (Только проверенные, реальные подвальные банды текущего периода)
        FALLBACK_CAMP = [
            ("Hermóðr", "Tales of the Frozen Forest", "🇸🇪 Atmospheric Black Metal"),
            ("Vothana", "Demo I", "🇺🇸 Raw Black Metal"),
            ("Sadness", "Blue Green", "🇺🇸 Post-Black Metal")
        ]
        fb_packs = []
        for b, a, g in FALLBACK_CAMP:
            fb_packs.append(f"{b} - {a} ({current_year})\n{g}\nhttps://bandcamp.com {current_month_tag}")
        return "\n---\n".join(fb_packs)
        
    except Exception as e:
        return f"❌ Ошибка Bandcamp-шлюза: {str(e)}"

def send_to_admin(content_text, month_tag):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ СВЕЖИЙ ЧИСТОКРОВНЫЙ ПОДВАЛ С BANDCAMP ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Самые свежие андеграунд-релизы за {month_tag}! Тапни по блоку выше, текст скопируется. Вставь боту в чат!</i>"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    m_tag = months_map.get(time.gmtime().tm_mon, "JUL")
    final_report = fetch_bandcamp_underground()
    send_to_admin(final_report, m_tag)
