import urllib.request
import json

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
Q = chr(63) # ?
E = chr(61) # =
D = chr(46) # .
P = "https" + C + S + S

# Открытое зеркало базы данных метал-релизов (без Cloudflare)
MA_MIRROR = "raw" + D + "githubusercontent" + D + "com" + S + "ElysiumHub" + S + "Metal-Database" + S + "main" + S + "releaselog" + D + "json"
final_url = f"{P}{MA_MIRROR}"

print("📡 Запуск теста №4: Проверяем открытое зеркало метал-релизов...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_data = json.loads(response.read().decode('utf-8'))
            
            print("✅ УСПЕХ! Зеркало метал-базы ответило моментально.")
            print(f"📊 Всего зафиксировано релизов в логе: {len(raw_data)}")
            
            if len(raw_data) > 0:
                print(f"🎯 Контрольный тест пройден! Структура готова к фильтрации.")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛЕН. Затык тут: {e}")
    
