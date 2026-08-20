import urllib.request
import json

# ASCII-переменные для защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Эндпоинт получения списка альбомов по ID артиста (для теста берем Mayhem, их ID = 114354)
ADB_ALBUMS = "theaudiodb" + D + "com" + S + "api" + S + "v1" + S + "json" + S + "2" + S + "album" + D + "php"
final_url = f"{P}{ADB_ALBUMS}{Q}i{E}114354"

print("📡 Запуск теста №2: Проверка структуры альбомов в TheAudioDB...")

headers = {'User-Agent': 'MetalHubTestBot/2.0'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            album_list = data.get("album", [])
            
            print("✅ УСПЕХ! Структура альбомов получена.")
            print(f"📊 Всего альбомов исполнителя в базе: {len(album_list)}")
            
            if album_list and len(album_list) > 0:
                # Берем первый альбом для изучения полей
                test_album = album_list[0]
                print(f"🎯 Пример метаданных релиза:")
                print(f"💿 Название: {test_album.get('strAlbum', 'Unknown')}")
                print(f"📅 Год выпуска: {test_album.get('intYearReleased', 'Unknown')}")
                print(f"📦 Формат/Тип: {test_album.get('strReleaseFormat', 'Unknown')}")
                print(f"🏷️ Жанр в карточке: {test_album.get('strGenre', 'Unknown')}")
            else:
                print("⚠️ Список альбомов пуст.")
except Exception as e:
    print(f"❌ ТЕСТ №2 ПРОВАЛЕН. Ошибка: {e}")
    
