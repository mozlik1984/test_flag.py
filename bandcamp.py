import os
import urllib.request
import urllib.parse
import json
import time

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Фирменная безопасная ASCII-склейка
S = chr(47); C = chr(58); Q = chr(63); E = chr(61); A = chr(38)
P = "https" + C + S + S
W = "www."

def fetch_bandcamp_final_api():
    print("🛰️ Попытка прорыва через скрытый JSON-шлюз Bandcamp...")
    
    # Скрытый шлюз дискавери, который отдает сырые данные для плееров
    url = P + W + "bandcamp.com" + S + "api" + S + "discover" + S + "3" + S + "get_web"
    
    # Просим у системы самый свежий блэк-метал (сортировка по дате добавления)
    payload = {
        "tags": ["black-metal"],
        "category": "album",
        "sort_key": "date",
        "page": 0
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Content-Type': 'application/json'
    }
    
    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return "❌ Сервер Bandcamp отклонил запрос плеера."
            
            data = json.loads(response.read().decode('utf-8'))
            
        results = data.get("items", [])
        if not results:
            return "🌑 На скрытой витрине Bandcamp сейчас пусто."
            
        packs = []
        for item in results[:7]:  # Берем ровно 7 самых свежих альбомов дня
            band = item.get("artist_name", "Unknown Artist").strip()
            album = item.get("title", "Unknown Album").strip()
            album_url = item.get("url", "").strip()
            
            if not album_url: continue
            
            # Принудительно чистим и склеиваем монолитную ссылку
            clean_url = album_url.split('?')[0]
            if "://" in clean_url and "://www." not in clean_url:
                clean_url = clean_url.replace("://", "://" + W)
                
            # Собираем красивую текстовую строку
            block = band + " - " + album + "\n🇳🇴 Black Metal\n" + clean_url
            packs.append(block)
            
        if packs:
            return "\n---\n".join(packs)
        return "🌑 Свежих релизов в пакете API не обнаружено."
        
    except Exception as e:
        return "❌ Ошибка прорыва через API: " + str(e)

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = "<b>⛓️ СВЕЖИЙ АВТОНОМНЫЙ БАНДКЭМП-УЛОВ ⛓️</b>\n\n<code>" + content_text + "</code>\n\n<i>👉 Скопируй в один тап! Вставь боту для наполнения кнопки СВЕЖЕЕ! Превью отключено.</i>"
    
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    report = fetch_bandcamp_api() if 'fetch_bandcamp_api' in globals() else fetch_bandcamp_final_api()
    send_to_admin(report)
    
