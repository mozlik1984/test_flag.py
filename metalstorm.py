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

# Открытый поисковый эндпоинт Spotify (через официальный открытый шлюз виджетов)
SPOTIFY_API = "open" + D + "spotify" + D + "com" + S + "oembed"
query = urllib.parse.quote("https://spotify.com") # Тестовый трек Dissection
final_url = f"{P}{SPOTIFY_API}{Q}url{E}{query}"

print("📡 Запуск разведки Spotify API v1.0...")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            
            print("✅ УСПЕХ! Сервер Spotify ответил моментально без блокировок.")
            print(f"🎸 Название трека в базе: {data.get('title')}")
            print(f"👤 Исполнитель/Автор: {data.get('author_name')}")
            print(f"🖼️ Ссылка на обложку: {data.get('thumbnail_url')}")
            print("🎯 ДИАГНОЗ: Шлюз открыт, структура данных идеальна для нашего бота.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
