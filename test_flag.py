import urllib.request
import urllib.parse
import re

BOT_TOKEN = "8615944325:AAFzRUmPbUzGtmBHUy4F4gp_gLd3dFBHAd0"
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58); P = "https" + C + S + S

def test_metal_archives():
    band_name = "Limbonic Art"
    encoded_name = urllib.parse.quote(band_name)
    url = P + "://metal-archives.com" + S + "search?searchString=" + encoded_name + "&type=band_name"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        match = re.search(r'<td><a href="https://://metal-archives.com/lists/[^"]+">([^<]+)</a></td>', html_content)
        if not match:
            match = re.search(r'<dt>Country of origin:</dt>\s*<dd><a href="[^"]+">([^<]+)</a></dd>', html_content)
            
        if match:
            country = match.group(1).strip()
            return f"✅ ГИТХАБ-ТЕСТ УСПЕШЕН!\n🌍 Группа: {band_name}\n🏴‍☠️ Страна на MA: {country}"
        else:
            return f"❌ Сеть Гитхаба работает, но регулярка промахнулась мимо HTML."
    except Exception as e:
        return f"💥 Гитхаб заблокирован Cloudflare: {str(e)}"

def send_result(report_text):
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': report_text}).encode('utf-8')
    req = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req)

if __name__ == "__main__":
    report = test_metal_archives()
    send_result(report)
