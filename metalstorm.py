import urllib.request
import json

# ASCII-переменные для защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Берем реальный открытый публичный метал-канал для теста коннекта
# Используем его публичную веб-витрину /s/
TARGET_CHANNEL = "metalprogression"
final_url = f"{P}t{D}me{S}s{S}{TARGET_CHANNEL}"

print(f"📡 Запуск теста v12.1: Сканируем веб-витрину Telegram-канала @{TARGET_CHANNEL}...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            print("✅ УСПЕХ! Сервер Telegram ответил моментально.")
            print(f"📊 Объем скачанного HTML: {len(html_content)} символов.")
            
            # Проверяем, видны ли текстовые блоки постов в HTML-разметке
            marker = "tgme_widget_message_text"
            if marker in html_content:
                posts_found = html_content.count(marker)
                print(f"🎯 ДИАГНОЗ: Обнаружено {posts_found} открытых постов для парсинга!")
            else:
                print("⚠️ ДИАГНОЗ: HTML получен, но блоки сообщений скрыты или защищены.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык здесь: {e}")
    
