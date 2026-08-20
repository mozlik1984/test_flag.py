import urllib.request
import urllib.parse
import json

# Абсолютная ASCII-защита протоколов и путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Открытый эндпоинт TheAudioDB API (тестовый ключ '2')
ADB_API = "theaudiodb" + D + "com" + S + "api" + S + "v1" + S + "json" + S + "2" + S + "search" + D + "php"

# Тестируем поиск группы Mayhem
band_name = "Mayhem"
encoded_band = urllib.parse.quote(band_name)
final_url = f"{P}{ADB_API}{Q}s{E}{encoded_band}"

print("📡 Запуск разведки TheAudioDB API v1.0...")

headers = {'User-Agent': 'MetalHubTestBot/1.0'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            artists = data.get("artists", [])
            
            print("✅ УСПЕХ! Сервер TheAudioDB ответил моментально.")
            
            if artists and len(artists) > 0:
                first_artist = artists[0]
                str_band = first_artist.get("strArtist", "Unknown")
                str_genre = first_artist.get("strGenre", "Unknown")
                str_country = first_artist.get("strCountry", "Unknown")
                
                print(f"🎯 Контрольный тест пройден успешно!")
                print(f"🎸 Найдена группа: {str_band}")
                print(f"💀 Основной жанр: {str_genre}")
                print(f"🌍 Страна: {str_country}")
            else:
                print("⚠️ Соединение есть, но группа не найдена в базе.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Ошибка подключения: {e}")
    
