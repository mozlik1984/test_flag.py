import urllib.request
import urllib.parse
import json
import time
import os
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

def mass_flag_generator():
    file_path = "bands_for_github.txt"
    if not os.path.exists(file_path):
        # Если файла нет, берем тестовую группу для проверки
        target_bands = ["Limbonic Art"]
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            target_bands = [line.strip() for line in f if line.strip()]
            
    headers = {'User-Agent': 'BlackMetalHubBot/7.0 ( mailto:Plokhomentov@example.com )'}
    packs = []
    
    # Чтобы Telegram не ругался на слишком длинные сообщения, 
    # мы обработаем первые 100 групп за один запуск (оптимальный пак для импорта)
    for band_name in target_bands[:100]:
        try:
            encoded_name = urllib.parse.quote(band_name)
            url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "artist" + "?query=" + encoded_name + "&fmt=json"
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    artists = data.get("artists", [])
                    
                    if artists and len(artists) > 0:
                        first_match = artists[0]
                        area_info = first_match.get("area", {})
                        country = area_info.get("name", "Norway")
                        
                        if country == "NO": country = "Norway"
                        if country == "SE": country = "Sweden"
                        if country == "FI": country = "Finland"
                        
                        flag = COUNTRY_TO_FLAG.get(country, "🇳🇴")
                        packs.append(f"{band_name}\n{flag}\nUPDATE")
            
            # Сетевой этикет MusicBrainz API (1 запрос в секунду)
            time.sleep(1.1)
        except:
            pass
            
    if packs:
        result_text = "\n---\n".join(packs)
        # Удаляем обработанные группы из файла, чтобы при следующем запуске пошли новые!
        with open(file_path, "w", encoding="utf-8") as f:
            for band in target_bands[100:]:
                f.write(f"{band}\n")
    else:
        result_text = "🌑 Все доступные группы из файла успешно обработаны!"
        
    api_url = P + "api.telegram.org" + S + "bot" + BOT_TOKEN + S + "sendMessage"
    formatted_msg = f"<b>⛓️ ПАК ФЛАГОВ СОБРАН (ТОП-100 БАНД) ⛓️</b>\n\n<code>{result_text}</code>\n\n<i>👉 Тапни по тексту выше — он скопируется. Вставь его мне в чат для авто-обновления базы Amvera! Остаток банд в очереди обновится на GitHub автоматически.</i>"
    
    data = urllib.parse.urlencode({'chat_id': ADMIN_CHAT_ID, 'text': formatted_msg, 'parse_mode': 'HTML', 'disable_web_page_preview': 'true'}).encode('utf-8')
    req_tg = urllib.request.Request(api_url, data=data)
    urllib.request.urlopen(req_tg)

if __name__ == "__main__":
    mass_flag_generator()
