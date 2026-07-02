import urllib.request
import re
import html

# --- НАСТРОЙКИ СВЯЗИ ---
# Токен и ID здесь больше НЕ НУЖНЫ! Скрипт просто сохранит файл на Гитхабе.
S = chr(47); C = chr(58); P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵"
}

def parse_metal_archives_rss():
    # Используем официальную RSS-ленту свежих альбомов Metal Archives. 
    # Она открыта, выдает чистый XML и не блокируется Cloudflare!
    url = P + "www.metal-archives.com" + S + "board" + S + "backend.php?mode=albums"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_content = response.read().decode('utf-8', errors='ignore')
            
        # Находим все элементы релизов в XML-ленте
        items = re.findall(r'<item>(.*?)</item>', xml_content, re.DOTALL)
        
        packs = []
        seen_albums = set()
        
        for item in items:
            title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
            desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item)
            
            if title_match and desc_match:
                # В ленте заголовок имеет вид: "Band Name - Album Name"
                full_title = html.unescape(title_match.group(1)).strip()
                desc_text = desc_match.group(1)
                
                # Фильтруем строго БЛЭК-МЕТАЛ полноформатники
                if "Black" in desc_text and "Full-length" in desc_text and " - " in full_title:
                    parts = full_title.split(" - ", 1)
                    band = parts[0].strip()
                    album = parts[1].strip()
                    
                    release_key = f"{band} - {album}".lower()
                    if release_key in seen_albums:
                        continue
                    seen_albums.add(release_key)
                    
                    # Пытаемся определить страну из описания
                    flag = "🇳🇴"
                    for country, emoji in COUNTRY_TO_FLAG.items():
                        if country in desc_text:
                            flag = emoji
                            break
                            
                    # Собираем строчку по твоему канону импорта (Июнь 2026)
                    block = f"{band} - {album} (2026)\n{flag} Black Metal\nhttps://youtube.com JUN"
                    packs.append(block)
                    
        if packs:
            result_text = "\n---\n".join(packs[:20]) # Берем топ-20 свежих релизов
        else:
            result_text = "🌑 Свежих проверенных релизов в ленте Metal Archives пока не обнаружено."
            
        # Записываем результат в текстовый файл, который бот заберет с Amvera!
        with open("june_2026.txt", "w", encoding="utf-8") as f:
            f.write(result_text)
            
        print("✅ Успешно сохранено в june_2026.txt!")
        
    except Exception as e:
        print(f"❌ Ошибка сбора ленты: {str(e)}")

if __name__ == "__main__":
    parse_metal_archives_rss()
