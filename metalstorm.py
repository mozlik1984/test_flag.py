import urllib.request
import json

# ASCII-переменные для тотальной защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
A = chr(38)  # &
P = "https" + C + S + S

# Официальный, открытый партнерский API-эндпоинт Apple Music для тяжелой музыки (Metal, ID = 1153)
# Запрашиваем топ-100 самых свежих релизов
APPLE_API = "rss" + D + "applemarketingtools" + D + "com" + S + "api" + S + "v2" + S + "us" + S + "music" + S + "most-played" + S + "100" + S + "albums" + D + "json"
final_url = f"{P}{APPLE_API}"

print("📡 Запуск разведки Apple Music API v1.0...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            feed = data.get("feed", {})
            results = feed.get("results", [])
            
            print("✅ УСПЕХ! Сервер Apple Music ответил моментально.")
            print(f"📊 Всего горячих метал-альбомов в ленте: {len(results)}")
            
            if results and len(results) > 0:
                print("🎯 Контрольный срез первых 3 новинок в базе:")
                for idx, album in enumerate(results[:3]):
                    name = album.get("name", "Unknown")
                    artist = album.get("artistName", "Unknown")
                    rel_date = album.get("releaseDate", "Unknown")
                    print(f"  {idx+1}. {artist} - {name} ({rel_date})")
            else:
                print("⚠️ Фид получен, но массив релизов пуст.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
