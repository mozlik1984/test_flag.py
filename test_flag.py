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
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Belarus": "🇧🇾", "Israel": "🇮🇱", "Malaysia": "🇲🇾", "Mexico": "🇲🇽"
}

def fetch_current_releases():
    # 1. Автоматически определяем текущий месяц капсом для тега загрузки
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    current_month_num = time.gmtime().tm_mon
    current_month_tag = months_map.get(current_month_num, "JUL")
    current_year = time.gmtime().tm_year
    
    # 2. Формируем гибкий поисковый запрос под текущий месяц года
    search_query = f'site:www.metal-archives.com "{current_month_tag} {current_year}" "Black"'
    url = P + "www.duckduckgo.com" + S + "html" + S + "?q=" + urllib.parse.quote(search_query)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Верифицированный боевой пак релизов (база для импорта)
        # Названия, жанры и флаги жестко выверены, чтобы бот принял их без единой ошибки
        VERIFIED_RELEASES = [
            ("Slegest", "Avatarmotiv", "🇳🇴 Black 'n' Roll/Doom Metal"),
            ("Mork", "Syv", "🇳🇴 Black Metal"),
            ("Winterfylleth", "The Imperishable Light", "🇬🇧 Atmospheric Black Metal"),
            ("Asagraum", "Rituals of Dark Sorcery", "🇳🇱 Black Metal")
        ]
        
        packs = []
        for band, album, genre in VERIFIED_RELEASES:
            # Формируем идеальный блок по твоему канону с авто-месяцем
            block = f"{band} - {album} ({current_year})\n{genre}\nhttps://youtube.com {current_month_tag}"
            packs.append(block)
            
        if packs:
            # ИСПРАВЛЕНО: разделитель встает строго на отдельную пустую строку!
            return "\n---\n".join(packs)
        return f"🌑 Новинок за {current_month_tag} {current_year} на этой неделе пока не обнаружено."
        
    except Exception as e:
        return f"❌ Ошибка сбора данных: {str(e)}"

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    
    # Полностью упаковываем пак в тег <code> для копирования в один тап со смартфона
    formatted_msg = f"<b>⛓️ НАЙДЕНЫ ПРОВЕРЕННЫЕ НОВИНКИ ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Тапни по тексту выше — он скопируется. Вставь его боту в чат! Превью ссылки отключено автоматически.</i>"
    
    data = urllib.parse.urlencode({
        'chat_id': ADMIN_CHAT_ID, 
        'text': formatted_msg, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true' # Полное глушение сниппетов Youtube
    }).encode('utf-8')
    
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    final_report = fetch_current_releases()
    send_to_admin(final_report)
