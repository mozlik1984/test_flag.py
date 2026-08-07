import os
import urllib.request
import urllib.parse
import re

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Твоя фирменная безопасная ASCII-склейка
S = chr(47); C = chr(58); W = "www."
P = "https" + C + S + S

def fetch_bandcamp_rss():
    print("🔥 Текстовый прорыв через RSS-ленту Bandcamp...")
    
    url = P + "www.bandcamp.com" + S + "tag" + S + "black-metal" + S + "feed.xml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return "❌ Сервер Bandcamp не ответил на запрос ленты."
            # Читаем как чистый текст
            html_text = response.read().decode('utf-8', errors='ignore')
            
        # Используем регулярные выражения, чтобы вытащить <title> и <link> из каждого <item>
        # Этот метод никогда не упадет из-за спецсимволов (&, <, >), так как ищет просто текст
        items = re.findall(r'<item>(.*?)</item>', html_text, re.DOTALL)
        
        if not items:
            return "Свежих релизов в ленте не обнаружено."
            
        packs = []
        for item in items[:7]: # Берем 7 самых свежих
            # Вытаскиваем название альбома/группы
            title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
            # Вытаскиваем ссылку
            link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
            
            if not title_match or not link_match:
                continue
                
            title_text = title_match.group(1).strip()
            album_url = link_match.group(1).strip()
            
            # Декодируем стандартные XML-замены вроде &amp; обратно в нормальный знак &
            title_text = title_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            title_text = title_text.replace('<![CDATA[', '').replace(']]>', '')
            album_url = album_url.replace('<![CDATA[', '').replace(']]>', '')
            
            # Чистим ссылку от хвостиков статистики
            clean_url = album_url.split('?')[0]
            
            # Твоя фирменная безопасная разбивка текста для копирования с телефона
            block = title_text + "\n🇳🇴 Black Metal\n" + clean_url
            packs.append(block)
            
        if packs:
            return "\n---\n".join(packs)
        return "Свежих релизов после фильтрации не обнаружено."
        
    except Exception as e:
        return "❌ Ошибка текстового разбора ленты: " + str(e)

def send_to_admin(content_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = "<b>⚙️ СВЕЖИЙ АВТОНОМНЫЙ БАНДКЭМП-УЛОВ ⚙️</b>\n\n<code>" + content_text + "</code>\n\n<i>Скопируй в один тап! Вставь боту для наполнения кнопки СВЕЖЕЕ!</i>"
    
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
    
