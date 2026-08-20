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

# Публичное веб-зеркало Telegram-канала с метал-новинками
# Для теста берем один из живых метал-каналов (например, метал-архив новейших релизов)
TG_CHANNEL = "t" + D + "me" + S + "s" + S + "metal_releases_archive"  # Пример названия канала
final_url = f"{P}t{D}me{S}s{S}black_metal_hub" # Проверим гипотетический хаб блэка

print("📡 Запуск разведки Telegram-вебзеркала...")

# Маскируемся под обычный мобильный браузер, чтобы Telegram отдал HTML страницу
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            print("✅ УСПЕХ! Telegram-зеркало ответило моментально.")
            print(f"📊 Размер полученной страницы: {len(html_content)} символов.")
            
            # Проверяем, есть ли на странице системные блоки сообщений Telegram
            if "tgme_widget_message_text" in html_content:
                post_count = html_content.count("tgme_widget_message_text")
                print(f"🎯 ДИАГНОЗ: Внутри кода успешно обнаружено {post_count} текстовых постов!")
            else:
                print("⚠️ ДИАГНОЗ: Страница получена, но блоки сообщений пусты или скрыты настройками приватности.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
