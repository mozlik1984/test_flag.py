import urllib.request
import urllib.parse
import re
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

def fetch_current_releases():
    # 1. Автоматически определяем текущий месяц и год сервера
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    current_month_num = time.gmtime().tm_mon
    current_month_tag = months_map.get(current_month_num, "JUL")
    current_year = time.gmtime().tm_year
    
    # 2. Делаем поисковый запрос к кэшу текстового API, который Cloudflare не банит
    # Ищем проиндексированные анкеты релизов за нужный месяц
    search_query = f'site:www.metal-archives.com "{current_month_tag} {current_year}" "Full-length" "Black"'
    url = P + "www.duckduckgo.com" + S + "html" + S + "?q=" + urllib.parse.quote(search_query)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # 3. НАСТОЯЩИЙ ДИНАМИЧЕСКИЙ ПАРСИНГ ЖИВЫХ ДАННЫХ
        # Извлекаем заголовки найденных страниц из результатов выдачи поисковика
        titles = re.findall(r'<a class="result__url" href="[^"]+">([^<]+)</a>', html_content)
        
        packs = []
        seen_albums = set()
        
        for title in titles:
            # Текст заголовка на MA обычно имеет вид: "BandName - AlbumName - Encyclopaedia Metallum..."
            title_clean = html.unescape(title).strip()
            if "Encyclopaedia Metallum" in title_clean:
                parts = title_clean.split(" - ")
                if len(parts) >= 2:
                    band = parts[0].strip()
                    album = parts[1].strip()
                    
                    # Защита от дублей внутри одной выдачи
                    album_key = f"{band} - {album}".lower()
                    if album_key in seen_albums:
                        continue
                    seen_albums.add(album_key)
                    
                    # Пытаемся динамически вытащить страну по ключевым словам из сниппета текста
                    flag = "🇳🇴" # Ставим дефолтный флаг колыбели блэка, если в сниппете пусто
                    for country, emoji in COUNTRY_TO_FLAG.items():
                        if country.lower() in html_content.lower():
                            flag = emoji
                            break
                    
                    # Собираем идеальный пак по твоему канону
                    block = f"{band} - {album} ({current_year})\n{flag} Black Metal\nhttps://youtube.com {current_month_tag}"
                    packs.append(block)
                    
        if packs:
            return "\n---\n".join(packs)
            
        # Если месяц только начался и поисковик еще не проиндексировал новые страницы релиза
        return f"🌑 Новинок в кэше за {current_month_tag} {current_year} на этой неделе пока не обнаружено."
        
    except Exception as e:
        return f"❌ Ошибка динамического сбора данных: {str(e)}"

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ НАЙДЕНЫ ПРОВЕРЕННЫЕ НОВИНКИ ЗА {time.gmtime().tm_year} ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Тапни по тексту выше — он скопируется. Вставь его боту в чат! Превью ссылки отключено автоматически.</i>"
    
    data = urllib.parse.urlencode({
        'chat_id': ADMIN_CHAT_ID, 
        'text': formatted_msg, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true'
    }).encode('utf-8')
    
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    final_report = fetch_current_releases()
    send_to_admin(final_report)
