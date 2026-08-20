import urllib.request

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
Q = chr(63) # ?
P = "https" + C + S + S

# Официальный и активный XML-фид Metal Storm
MS_XML = "metalstorm.net" + S + "xml" + S + "rss_releases.xml"
final_url = f"{P}{MS_XML}"

print("📡 Запуск разведки официального Metal Storm XML...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_xml = response.read().decode('utf-8', errors='ignore')
            
            print("✅ УСПЕХ! Свежий фид Metal Storm ответил моментально.")
            print(f"📊 Размер фида: {len(raw_xml)} символов.")
            
            if "item" in raw_xml.lower():
                print("🎯 ДИАГНОЗ: Внутри фида успешно найдены блоки релизов!")
            else:
                print("⚠️ ДИАГНОЗ: Ответ пустой или структура фида изменилась.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
