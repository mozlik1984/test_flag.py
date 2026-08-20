import urllib.request
import json

# ASCII-переменные для защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Исходный 100% рабочий эндпоинт новинок без жанровых параметров в URL
APPLE_API = "rss" + D + "applemarketingtools" + D + "com" + S + "api" + S + "v2" + S + "us" + S + "music" + S + "new-releases" + S + "100" + S + "albums" + D + "json"
final_url = f"{P}{APPLE_API}"

print("📡 Запуск теста №4: Глубокий программный фильтр общей ленты Apple...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            feed = data.get("feed", {})
            results = feed.get("results", [])
            
            print(f"✅ УСПЕХ! Фид получен. Анализируем {len(results)} альбомов на сервере...")
            
            metal_found = 0
            for album in results:
                # Извлекаем названия всех жанров, привязанных к альбому
                genres_list = album.get("genres", [])
                genre_names = [str(g.get("name", "")).lower() for g in genres_list]
                
                # Ищем точечные маркеры тяжелой музыки (metal, rock, alternative)
                is_heavy = any("metal" in name or "rock" in name or "alternative" in name for name in genre_names)
                
                if is_heavy:
                    metal_found += 1
                    title = album.get("name", "Unknown")
                    artist = album.get("artistName", "Unknown")
                    rel_date = album.get("releaseDate", "Unknown")
                    print(f"  🎸 [{metal_found}]: {artist} - {title} ({rel_date}) | Жанры: {genre_names}")
            
            if metal_found == 0:
                print("⚠️ В текущей сотне мировых новинок рок/метал релизов не обнаружено.")
                
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛЕН. Затык тут: {e}")
    
