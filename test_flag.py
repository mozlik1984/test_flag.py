import urllib.request
import urllib.parse
import re

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

def start_github_proxy():
    band_name = "Limbonic Art" 
    encoded_name = urllib.parse.quote(band_name)
    
    # Оригинальная цель
    target_url = P + "www.metal-archives.com" + S + "search?searchString=" + encoded_name + "&type=band_name"
    
    # --- БРОНЕБОЙНЫЙ ШЛЮЗ ПРОТИВ CLOUDFLARE ---
    # Пускаем запрос через профессиональный прокси-дешифратор (ScraperAPI)
    # Этот ключ полностью берет на себя обход 403 ошибки!
    SCRAPER_API_KEY = "3b08e2f89f36f9a0c7c88fb7310d2105"
    proxy_url = f"http://scraperapi.com?api_key={SCRAPER_API_KEY}&url=" + urllib.parse.quote(target_url)
    # ------------------------------------------
    
    try:
        req = urllib.request.Request(proxy_url)
        with urllib.request.urlopen(req, timeout=25) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Наш тройной парсинг чистой страны из оригинального HTML кода
        match = re.search(r'<td><a href="[^"]+">[^<]+</a>\s*\(([^)]+)\)</td>', html_content)
        if not match:
            match = re.search(r'<dt>Country of origin:</dt>\s*<dd><a href="[^"]+">([^<]+)</a></dd>', html_content)
            
        if match:
            country = match.group(1).strip()
            flag = COUNTRY_TO_FLAG.get(country, "")
            report = f"PROXY_SUCCESS|{band_name}|{country}|{flag}"
        else:
            report = f"PROXY_ERROR|{band_name}|Cloudflare обошли, но группа не найдена на сайте"
            
    except Exception as e:
        report = f"PROXY_ERROR|{band_name}|Анти-бот защита не пробита: {str(e)}"
        
    # Отправляем чистый результат обратно в твоего бота на Amvera
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': report}).encode('utf-8')
    req_tg = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req_tg)

if __name__ == "__main__":
    start_github_proxy()
