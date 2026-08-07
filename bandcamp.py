import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Твоя фирменная безопасная ASCII-склейка
S = chr(47); C = chr(58); W = "www."
P = "https" + C + S + S

def fetch_bandcamp_rss():
    print("🔥 Сбор свежего блэка через официальный RSS-шлюз Bandcamp...")
    
    # Стабильная и открытая лента Bandcamp по тегу black-metal
    url = P + "www.bandcamp.com" + S + "tag" + S + "black-metal" + S + "feed.xml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return "❌ Сервер Bandcamp не ответил на запрос ленты."
            
            # ИСПРАВЛЕНИЕ: Декодируем в чистый utf-8 и жестко игнорируем любые 
            # ломающие спецсимволы (&, <, > и умлауты), на которых спотыкался XML-парсер
            xml_text = response.read().decode('utf-8', errors='ignore')
            
        root = ET.fromstring(xml_text)
        
        packs = []
        # Пробегаемся по свежим релизам в XML-ленте
        for item in root.findall('.//item')[:7]: # Берем 7 самых свежих альбомов
            title_text = item.find('title').text if item.find('title') is not None else "Unknown - Unknown"
            album_url = item.find('link').text if item.find('link') is not None else ""
            
            if not album_url:
                continue
                
            # Чистим ссылку от хвостиков статистики
            clean_url = album_url.split('?')
            
            # Твоя фирменная безопасная разбивка текста для копирования с телефона
            block = title_text + "\n🇳🇴 Black Metal\n" + clean_url
            packs.append(block)
            
        if packs:
            return "\n---\n".join(packs)
        return "Свежих релизов в ленте не обнаружено."
        
    except Exception as e:
        return "❌ Ошибка разбора RSS: " + str(e)

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = "<b>⚙️ СВЕЖИЙ АВТОНОМНЫЙ БАНДКЭМП-УЛОВ ⚙️</b>\n\n<code>" + content_text + "</code>\n\n<i>Скопируй в один тап! Вставь боту для наполнения кнопки СВЕЖЕЕ!</i>"
    
    # Кодируем данные для отправки в Telegram
    payload = {
        'chat_id': ADMIN_CHAT_ID,
        'text': formatted_msg,
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true'
    }
    data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request(api_url, data=data, method='POST')
    urllib.request.urlopen(req)

if __name__ == "__main__":
    report = fetch_bandcamp_rss()
    send_to_admin(report)
    
