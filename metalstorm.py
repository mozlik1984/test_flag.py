import urllib.request
import urllib.parse
import json

# ASCII-переменные для защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Эндпоинт поиска артистов по жанру
ADB_GENRE_SEARCH = "theaudiodb" + D + "com" + S + "api" + S + "v1" + S + "json" + S + "2" + S + "search" + D + "php"
genre_query = urllib.parse.quote("Black Metal")
final_url = f"{P}{ADB_GENRE_SEARCH}{Q}g{E}{genre_query}"

print("📡 Запуск Теста №3: Проверка поиска групп по жанру Black Metal...")

headers = {'User-Agent': 'MetalHubTestBot/3.0'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            artists = data.get("artists", [])
            
            print("✅ УСПЕХ! Список блэк-метал групп получен.")
            if artists:
                print(f"📊 Всего найдено групп в выборке: {len(artists)}")
                # Выведем первые три группы для проверки
                for idx, artist in enumerate(artists[:3]):
                    name = artist.get("strArtist", "Unknown")
                    country = artist.get("strCountry", "Unknown")
                    print(f"  {idx+1}. {name} ({country})")
            else:
                print("⚠️ База вернула пустой список для этого эндпоинта.")
except Exception as e:
    print(f"❌ ТЕСТ №3 ПРОВАЛЕН. Ошибка: {e}")
    
