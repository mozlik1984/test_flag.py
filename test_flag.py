import urllib.request
import urllib.parse
import re
import json
import html

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
    # Гитхаб сам берет имя группы, которую ты затребовал!
    # Для теста жестко ставим Limbonic Art, затем автоматизируем
    band_name = "Limbonic Art" 
    
    encoded_name = urllib.parse.quote(band_name)
    url = P + "www.metal-archives.com" + S + "search?searchString=" + encoded_name + "&type=band_name"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Тройной парсинг страны без косяков и цифр
        match = re.search(r'<td><a href="[^"]+">[^<]+</a>\s*\(([^)]+)\)</td>', html_content)
        if not match:
            match = re.search(r'<dt>Country of origin:</dt>\s*<dd><a href="[^"]+">([^<]+)</a></dd>', html_content)
            
        if match:
            country = match.group(1).strip()
            flag = COUNTRY_TO_FLAG.get(country, "")
            report = f"PROXY_SUCCESS|{band_name}|{country}|{flag}"
        else:
            report = f"PROXY_ERROR|{band_name}|Страна не найдена в HTML верстке"
            
    except Exception as e:
        report = f"PROXY_ERROR|{band_name}|Ошибка Cloudflare: {str(e)}"
        
    # Шлюз отправляет чистый ответ напрямую в твоего бота на Amvera!
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': report}).encode('utf-8')
    req_tg = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req_tg)

if __name__ == "__main__":
    start_github_proxy()
