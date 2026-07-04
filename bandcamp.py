import os
import urllib.request
import urllib.parse
import json
import time
import re

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Ваша фирменная ASCII-склейка для монолитных ссылок на мобилке
S = chr(47); C = chr(58); Q = chr(63); E = chr(61); A = chr(38)
P = "https" + C + S + S
W = "www."

def fetch_bandcamp_live_radar():
    print("🛰️ Запуск живого радара Bandcamp... Ищем свежий блэк-метал!")
    
    # URL страницы discover
    url = P + W + "bandcamp.com" + S + "discover" + S + "black-metal"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Вытаскиваем скрытый JSON с данными всех альбомов на странице
        blob_match = re.search(r'data-blob="([^"]+)"', html_content)
        if not blob_match:
            return "❌ Не удалось прочитать карту данных Bandcamp (возможно, изменилась верстка)."
            
        # Декодируем HTML-символы в чистый текст JSON
        raw_json = urllib.parse.unquote(blob_match.group(1)).replace('&quot;', '"').replace('&amp;', '&')
        data = json.loads(raw_json)
        
        # Пробиваем путь до списка альбомов в структуре Bandcamp
        discover_data = data.get("discover", {})
        results = discover_data.get("results", [])
        
        if not results:
            return "🌑 Свежих альбомов на витрине Bandcamp прямо сейчас не обнаружено."
            
        packs = []
        for item in results[:8]: # Берем топ-8 самых свежих релизов с витрины
            band = item.get("artist_name", "Unknown Band").strip()
            album = item.get("title", "Unknown Album").strip()
            album_url = item.get("url", "").strip()
            
            if not album_url: continue
            
            # Принудительно собираем красивую ссылку с www. через вашу склейку
            if "bandcamp.com" in album_url:
                clean_url = album_url.split('?')[0] # Отрезаем мусор
                if "://www." not in clean_url:
                    clean_url = clean_url.replace("://", "://" + W)
            else:
                clean_url = P + W + "bandcamp.com" + album_url
                
            # Формируем красивый блок. Страну ставим дефолтную, так как в быстром списке её нет
            block = band + " - " + album + "\n🇳🇴 Black Metal\n" + clean_url
            packs.append(block)
            
        if packs:
            return "\n---\n".join(packs)
        return "🌑 Витрина Bandcamp пуста."
        
    except Exception as e:
        return "❌ Ошибка живого радара: " + str(e)

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    
    # Красивый заголовок без привязки к старым датам
    formatted_msg = "<b>⛓️ СВЕЖИЙ АВТОНОМНЫЙ БАНДКЭМП-УЛОВ ⛓️</b>\n\n<code>" + content_text + "</code>\n\n<i>👉 Скопируй в один тап! Вставь боту в чат для наполнения кнопки СВЕЖЕЕ! Превью отключено.</i>"
    
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    report = fetch_bandcamp_live_radar()
    send_to_admin(report)
    
