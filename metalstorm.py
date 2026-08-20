import urllib.request
import time

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
Q = chr(63) # ?
E = chr(61) # =
D = chr(46) # .
P = "https" + C + S + S

# Прямой и легальный фид конкретного YouTube-канала (Black Metal Promotion)
YT_FEED = "www" + D + "youtube" + D + "com" + S + "feeds" + S + "videos" + D + "xml" + Q + "channel_id" + E + "UCvC_vObCtd-SihWvCEX9Z3w"
final_url = f"{P}{YT_FEED}"

print("📡 Запуск разведки YouTube RSS-фида канала Black Metal Promotion...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_xml = response.read().decode('utf-8', errors='ignore')
            
            print("✅ УСПЕХ! YouTube ответил моментально и отдал данные.")
            print(f"📊 Размер полученного фида: {len(raw_xml)} символов.")
            
            # Проверяем структуру: ищем теги <entry> (это видеоролики)
            if "<entry>" in raw_xml:
                # Считаем количество свежих видео в ленте
                video_count = raw_xml.count("<entry>")
                print(f"🎯 ДИАГНОЗ: В ленте успешно обнаружено {video_count} свежих видео!")
            else:
                print("⚠️ ДИАГНОЗ: Ответ получен, но свежих видео внутри структуры нет.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
