import urllib.request

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
Q = chr(63) # ?
E = chr(61) # =
D = chr(46) # .
A = chr(38) # &
P = "https" + C + S + S

# Абсолютно точный и живой RSS эндпоинт YouTube для каналов
YT_RSS = "www" + D + "youtube" + D + "com" + S + "feeds" + S + "videos" + D + "xml" + Q + "channel_id" + E + "UCvC_vObCtd-SihWvCEX9Z3w"
final_url = f"{P}{YT_RSS}"

print("📡 Запуск теста №3: Проверяем точный RSS-фид Black Metal Promotion...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_xml = response.read().decode('utf-8', errors='ignore')
            
            print("✅ УСПЕХ! Фид полностью получен.")
            print(f"📊 Размер XML: {len(raw_xml)} символов.")
            
            # Проверяем наличие видео в разметке Гугла
            if "<entry>" in raw_xml:
                video_count = raw_xml.count("<entry>")
                print(f"🎯 ДИАГНОЗ: Найдено {video_count} свежих блэк-метал релизов!")
                
                # Вытащим для диагностики название самого последнего видео
                title_start = raw_xml.find("<title>")
                title_start = raw_xml.find("<title>", title_start + 1) # Пропускаем название канала
                title_end = raw_xml.find("</title>", title_start)
                if title_start != -1 and title_end != -1:
                    print(f"🎸 Последний релиз в ленте: {raw_xml[title_start+7:title_end]}")
            else:
                print("⚠️ Структура фида пуста.")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛЕН. Затык тут: {e}")
    
