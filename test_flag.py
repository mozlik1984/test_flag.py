import urllib.request
import urllib.parse
import json
import time
import re

# --- КОНФИГУРАЦИЯ СВЯЗИ ---
BOT_TOKEN = "8615944325:AAFzRUmPbUzGtmBHUy4F4gp_gLd3dFBHAd0"
ADMIN_CHAT_ID = 5002053185
DISCOGS_TOKEN = "pMJGQnTxUPhrxUHCFytavDSnxAOiBwhPjjxuDtue"

S = chr(47); C = chr(58); P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵"
}

def fetch_discogs_releases():
    # --- НАСТРОЙКА МАШИНЫ ВРЕМЕНИ (МАРТ 2026) ---
    current_month_tag = "MAR"
    month_name_full = "march"  # Ищем упоминание месяца текстом
    month_num_alt = "03"       # Ищем числовой формат
    current_year = 2026
    # ----------------------------------------------------
    
    url = P + "api.discogs.com" + S + "database" + S + "search"
    params = {
        "style": "Black Metal",
        "type": "release",
        "format": "Album",
        "year": str(current_year),
        "sort": "year",        # Сортировка по году релиза
        "sort_order": "desc",  # Сначала самые новые поступления
        "per_page": 100        # Расширяем выборку до 100, чтобы точно зацепить месяц
    }
    
    headers = {
        "User-Agent": "BlackMetalHubBot/4.0",
        "Authorization": f"Discogs token={DISCOGS_TOKEN}"
    }
    
    try:
        full_url = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(full_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get("results", [])
                
                packs = []
                seen_releases = set()
                
                for item in results:
                    # УМНЫЙ ГИБКИЙ ФИЛЬТР ДАТЫ
                    release_date = str(item.get("date", "")).lower()
                    
                    # Если в поле даты вообще ничего нет, или там просто год 2026 без уточнений,
                    # мы временно пропускаем строгий фильтр, чтобы дать тебе увидеть свежий живой улов
                    is_valid_month = (month_name_full in release_date) or (f"-{month_num_alt}-" in release_date) or (release_date == "2026")
                    
                    if not is_valid_month:
                        continue

                    title = item.get("title", "")
                    if " - " in title:
                        parts = title.split(" - ", 1)
                        band = parts[0].strip()
                        album = parts[1].strip()
                        
                        # Очищаем технический мусор Discogs списков
                        band = re.sub(r'\s*\(\d+\)$', '', band).replace('*', '').strip()
                        album = re.sub(r'\s*\(\d+\)$', '', album).replace('*', '').strip()
                        
                        release_key = f"{band} - {album}".lower()
                        if release_key in seen_releases:
                            continue
                        seen_releases.add(release_key)
                        
                        country = item.get("country", "Norway")
                        flag = COUNTRY_TO_FLAG.get(country, "🇳🇴")
                        
                        block = f"{band} - {album} ({current_year})\n{flag} Black Metal\nhttps://youtube.com {current_month_tag}"
                        packs.append(block)
                        
                if packs:
                    # Возвращаем первые 15 самых свежих очищенных релизов
                    return "\n---\n".join(packs[:15])
                    
        return f"🌑 Релизов за {current_month_tag} {current_year} с точным тегом даты не найдено."
        
    except Exception as e:
        return f"❌ Ошибка Discogs API: {str(e)}"

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ НАЙДЕНЫ СВЕЖИЕ РЕЛИЗЫ ИЗ БАЗЫ DISCOGS ⛓️</b>\n\n<code>{content_text}</code>\n\n<i>👉 Тапни по тексту выше — он скопируется. Вставь его боту в чат! Превью отключено.</i>"
    
    data = urllib.parse.urlencode({
        'chat_id': ADMIN_CHAT_ID, 
        'text': formatted_msg, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true'
    }).encode('utf-8')
    
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    final_report = fetch_discogs_releases()
    send_to_admin(final_report)
