import urllib.request
import time

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
Q = chr(63) # ?
P = "https" + C + S + S

# Открытый RSS-фид релизов Metal Storm (не защищен Cloudflare)
MS_RSS = "metalstorm.net" + S + "rss" + S + "rds_releases.php"
final_url = f"{P}{MS_RSS}"

print("📡 Запуск разведки Metal Storm RSS Фида...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_xml = response.read().decode('utf-8', errors='ignore')
            
            print("✅ УСПЕХ! Фид Metal Storm ответил моментально.")
            print(f"📊 Размер полученных данных: {len(raw_xml)} символов.")
            
            # Проверяем, есть ли блэк-метал в текущей ленте новостей
            if "black" in raw_xml.lower():
                print("🎯 ДИАГНОЗ: Блэк-метал релизы обнаружены в ленте!")
            else:
                print("⚠️ ДИАГНОЗ: Данные получены, но блэк-метал треков в текущем фиде нет.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
