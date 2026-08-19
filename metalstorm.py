import urllib.request
import urllib.parse
import json

# ASCII-переменные защиты путей
S = chr(47) # /
C = chr(58) # :
P = "https" + C + S + S
MS_BASE = "metalstorm.net" + S + "events" + S + "releases.php"

# Скрытый прокси-обходчик Cloudflare (CORS Proxy)
PROXY = "api.allorigins.win" + S + "get" + Q + "url" + E

# Сборка финальной ссылки через прокси
target_url = f"{P}{MS_BASE}"
final_url = f"{P}{PROXY}{urllib.parse.quote(target_url)}"

print(f"📡 Запуск разведки... Стучимся на Metal Storm через прокси-барьер.")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        if response.status == 200:
            raw_data = json.loads(response.read().decode('utf-8'))
            html_content = raw_data.get("contents", "")
            
            print(f"✅ УСПЕХ! Прокси вернул данные.")
            print(f"📊 Размер полученного HTML: {len(html_content)} символов.")
            
            # Ищем, есть ли в коде упоминание таблицы релизов
            if "<table" in html_content:
                print("🎯 ДИАГНОЗ: Таблица релизов успешно обнаружена в коде!")
            else:
                print("⚠️ ДИАГНОЗ: Ответ получен, но структуры таблицы внутри нет.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
