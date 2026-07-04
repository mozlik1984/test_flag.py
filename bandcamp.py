import os
import urllib.request
import urllib.parse
import time
import re

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Фирменная склейка, чтобы ссылки не бились на экране мобильного
S = chr(47); C = chr(58)
P = "https" + C + S + S
W = "www."

def fetch_bandcamp_radar():
    print("🛰️ Живой радар сканирует Bandcamp...")
    
    # Лезем на открытую страницу тега, где лежат все свежие поджанры
    url = P + W + "bandcamp.com" + S + "tag" + S + "black-metal"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        packs = []
        # Простейший поиск карточек: вытаскивает ссылку, название альбома и группу
        items = re.findall(r'href="([^"]+album=[^"]+)"[^>]*>.*?<div class="title">([^<]+)</div>.*?<div class="artist">([^<]+)</div>', html, re.DOTALL)
        
        if not items:
            # Запасной простой паттерн, если первый не сработает
            items = re.findall(r'href="([^"]+album=[^"]+)">([^<]+)</a>\s*by\s*<span class="artist">([^<]+)</span>', html)

        for album_url, album_name, band_name in items[:7]:
            band = band_name.strip()
            album = album_name.strip()
            
            # Собираем красивую монолитную ссылку
            if not album_url.startswith("http"):
                album_url = "https:" + album_url if album_url.startswith("//") else P + W + "bandcamp.com" + album_url
                
            clean_url = album_url.split('?')[0] # убираем мусор из хвоста ссылки
            
            # Автоматически определяем поджанр по тексту страницы (атмо, депрессив и т.д.)
            subgenre = "Black Metal"
            if "atmospheric" in html.lower(): subgenre = "Atmospheric Black Metal"
            elif "depressive" in html.lower() or "dsbm" in html.lower(): subgenre = "Depressive Black Metal"
            elif "symphonic" in html.lower(): subgenre = "Symphonic Black Metal"
            
            packs.append(band + " - " + album + "\n🇳🇴 " + subgenre + "\n" + clean_url)
            
        if packs: 
            return "\n---\n".join(packs)
        return "🌑 Свежего блэка на витрине Bandcamp прямо сейчас не найдено."
        
    except Exception as e:
        return "❌ Ошибка радара: " + str(e)

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = "<b>⛓️ СВЕЖИЙ АВТОНОМНЫЙ БАНДКЭМП-УЛОВ ⛓️</b>\n\n<code>" + content_text + "</code>\n\n<i>👉 Скопируй в один тап! Вставь боту для наполнения кнопки СВЕЖЕЕ! Превью отключено.</i>"
    
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    report = fetch_bandcamp_radar()
    send_to_admin(report)
    
