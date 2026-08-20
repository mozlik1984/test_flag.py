import urllib.request
import json

# ASCII-переменные защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Рабочий эндпоинт 100 свежих релизов
APPLE_API = "rss" + D + "applemarketingtools" + D + "com" + S + "api" + S + "v2" + S + "us" + S + "music" + S + "new-releases" + S + "100" + S + "albums" + D + "json"
final_url = f"{P}{APPLE_API}"

print("📡 Запуск теста №3: Сканирование 100 новинок Apple Music с поиском метала...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            feed = data.get("feed", {})
            results = feed.get("results", [])
            
            print(f"✅ Данные получены! Начинаем поиск тяжелых жанров из 100 позиций...")
            
            found_count = 0
            for album in results:
                genres = [str(g.get("name", "")).lower() for g in album.get("genres", [])]
                
                # Ищем любые упоминания тяжелой музыки в массиве жанров релиза
                is_heavy = any("metal" in g or "rock" in g or "alternative" in g for g in genres)
                
                if is_heavy:
                    found_count += 1
                    name = album.get("name", "Unknown")
                    artist = album.get("artistName", "Unknown")
                    rel_date = album.get("releaseDate", "Unknown")
                    print(f"  🎯 Найдено [{found_count}]: {artist} - {name} ({rel_date}) | Жанры: {genres}")
            
            if found_count == 0:
                print("⚠️ В текущей сотне новинок рок/метал релизов не обнаружено.")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛЕН. Затык тут: {e}")
    
