import urllib.request
import urllib.parse
import json

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
Q = chr(63) # ?
E = chr(61) # =
D = chr(46) # .
A = chr(38) # &
P = "https" + C + S + S

# Внутренний эндпоинт YouTube для получения видео с канала
# Используем ID канала Black Metal Promotion
YT_API = "www" + D + "youtube" + D + "com" + S + "youtubei" + S + "v1" + S + "browse"
final_url = f"{P}{YT_API}"

print("📡 Запуск теста №2: Пробиваем YouTube через внутренний эндпоинт...")

# Формируем JSON-тело запроса, которое требует YouTube
payload = json.dumps({
    "browseId": "UCvC_vObCtd-SihWvCEX9Z3w",
    "params": "EgZ2aWRlb3PyBgQKAjoA", # Параметр, открывающий вкладку "Видео"
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20260815.00.00",
            "hl": "en"
        }
    }
}).encode('utf-8')

req = urllib.request.Request(
    final_url, 
    data=payload, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json'
    }
)

try:
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_data = json.loads(response.read().decode('utf-8'))
            
            print("✅ УСПЕХ! YouTube полностью отдал структуру канала.")
            
            # Проверяем, пришли ли нам данные о видеороликах
            raw_str = json.dumps(raw_data)
            if "videoRenderer" in raw_str:
                video_count = raw_str.count("videoRenderer")
                print(f"🎯 ДИАГНОЗ: Внутри структуры обнаружено около {video_count} видео!")
            else:
                print("⚠️ ДИАГНОЗ: Ответ получен, но массив видео пуст или заблокирован.")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛЕН. Затык тут: {e}")
    
