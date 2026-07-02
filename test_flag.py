import urllib.request
import urllib.parse
import re
import html

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
    "Belarus": "🇧🇾", "Israel": "🇮🇱", "Malaysia": "🇲🇾", "Mexico": "🇲🇽"
}

def fetch_current_releases():
    # --- НАСТРОЙКА МАШИНЫ ВРЕМЕНИ (СТРОГО ИЮНЬ 2026) ---
    current_month_tag = "JUN"
    current_year = 2026
    # ----------------------------------------------------
    
    # Формируем точечный поисковый запрос к кэшу текстового каталога
    search_query = f'site:www.metal-archives.com "{current_month_tag} {current_year}" "Full-length" "Black"'
    url = P + "www.duckduckgo.com" + S + "html" + S + "?q=" + urllib.parse.quote(search_query)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Находим все заголовки проиндексированных страниц релизов
        titles = re.findall(r'<a class="result__url" href="[^"]+">([^<]+)</a>', html_content)
        
        packs = []
        seen_albums = set()
        
        for title in titles:
            title_clean = html.unescape(title).strip()
            # Нам нужны только анкеты релизов с Metal Archives
            if "Encyclopaedia Metallum" in title_clean:
                parts = title_clean.split(" - ")
                if len(parts) >= 2:
                    band = parts[0].strip()
                    album = parts[1].strip()
                    
                    # Отсекаем дубликаты в поисковой выдаче
                    album_key = f"{band} - {album}".lower()
                    if album_key in seen_albums:
                        continue
                    seen_albums.add(album_key)
                    
                    # Пытаемся автоматически вытащить страну по ключевым словам из кэша
                    flag = "🇳🇴"  # Дефолтный флаг, если в кэше пусто
                    for country, emoji in COUNTRY_TO_FLAG.items():
                        if country.lower() in html_content.lower():
                            flag = emoji
                            break
                    
                    # Собираем идеальную строчку по твоему канону массового импорта
                    block = f"{band} - {album} ({current_year})\n{flag} Black Metal\nhttps://youtube.com {current_month_tag}"
                    packs.append(block)
                    
        if packs:
            # Склеиваем через каноничную пустую строку и ---
            return "\n---\n".join(packs)
            
        return f"🌑 Новинок в кэше за {current_month_tag} {current_year} на этой неделе пока не обнаружено."
        
    except Exception as e:
        return f"❌ Ошибка динамического сбора данных: {str(e)}"

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    
    # Упаковываем весь пак в тег <code>, чтобы на телефоне копировать в ОДИН ТАП
    formatted_msg = f"<b>⛓️ НАЙДЕНЫ РЕАЛЬНЫЕ НОВИНКИ ЗА ИЮНЬ 2026 ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Просто нажми на блок выше — текст скопируется. Вставь его боту в чат! Ютуб-превью отключено.</i>"
    
    data = urllib.parse.urlencode({
        'chat_id': ADMIN_CHAT_ID, 
        'text': formatted_msg, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true' # Полное глушение превьюшек Youtube
    }).encode('utf-8')
    
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    final_report = fetch_current_releases()
    send_to_admin(final_report)
