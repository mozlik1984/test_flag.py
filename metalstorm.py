import urllib.request
import urllib.parse
import json
import time

# ASCII-переменные для защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
A = chr(38)  # &
P = "https" + C + S + S

D_API = "api" + D + "discogs" + D + "com" + S + "database" + S + "search"

# Тестируем релиз Профан Буриал (он легальный)
query_str = "Profane Burial Desolate Echoes of Turmoil"
encoded_query = urllib.parse.quote(query_str)
final_url = f"{P}{D_API}{Q}q{E}{encoded_query}{A}type{E}release"

print("📡 Тест Фильтра v8.0: Проверка чтения лейблов на Discogs...")
headers = {'User-Agent': 'MetalHubValidatorApp/5.0'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get("results", [])
            
            print("✅ УСПЕХ! Ответочка от Discogs пришла.")
            if results:
                first_item = results[0]
                # Вытягиваем лейбл из массива результатов
                labels = first_item.get("label", [])
                formats = first_item.get("format", [])
                
                print(f"🎯 Метаданные релиза найдены:")
                print(f"🏢 Издатель (Label): {labels}")
                print(f"📦 Форматы издания: {formats}")
            else:
                print("⚠️ Релиз не найден в базе поисковика.")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛЕН. Ошибка: {e}")
    
