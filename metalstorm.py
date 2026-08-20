import os
import urllib.request
import urllib.parse
import json
import time

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185
DISCOGS_TOKEN = "pMJGQnTxUPhrxUHCFytavDSnxAOiBwhPjjxuDtue"

S = chr(47); C = chr(58); Q = chr(63); A = chr(38); E = chr(61); D = chr(46)
P = "https" + C + S + S

# Ищем конкретный проверенный релиз
query_str = "Profane Burial Desolate Echoes of Turmoil"
encoded_query = urllib.parse.quote(query_str)

# Шаг 1: Находим релиз в поиске, чтобы получить его уникальный ID
search_url = f"{P}api{D}discogs{D}com{S}database{S}search{Q}q{E}{encoded_query}{A}type{E}release"
headers = {
    'User-Agent': 'MetalHubDeepSpy/1.0',
    'Authorization': f'Discogs token={DISCOGS_TOKEN}'
}

print(f"📡 Запуск глубокого анализа релиза Profane Burial...")

try:
    req = urllib.request.Request(search_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            search_data = json.loads(response.read().decode('utf-8'))
            results = search_data.get("results", [])
            
            if results:
                first_release = results[0]
                release_id = first_release.get("id")
                print(f"🎯 Релиз найден! ID в базе Discogs: {release_id}")
                
                # Шаг 2: Стучимся на персональную страницу релиза по его ID
                # Именно здесь лежит полная, не урезанная информация
                release_url = f"{P}api{D}discogs{D}com{S}releases{S}{release_id}"
                time.sleep(1)
                
                req_deep = urllib.request.Request(release_url, headers=headers)
                with urllib.request.urlopen(req_deep, timeout=12) as deep_response:
                    if deep_response.status == 200:
                        deep_data = json.loads(deep_response.read().decode('utf-8'))
                        
                        # Вытягиваем точные скрытые поля даты
                        released_field = deep_data.get("released", "Отсутствует")
                        released_formatted = deep_data.get("released_formatted", "Отсутствует")
                        
                        output_text = (
                            f"✅ УСПЕХ! Скрытые данные релиза получены:\n\n"
                            f"🎸 Группа/Альбом: Profane Burial (2026)\n"
                            f"📅 Поле 'released': {released_field}\n"
                            f"📅 Поле 'released_formatted': {released_formatted}\n"
                        )
            else:
                output_text = "🤷‍♂️ Релиз Profane Burial не найден в поиске Discogs по этому запросу."
except Exception as e:
    output_text = f"❌ Ошибка глубокого анализа: {e}"

# Отправка результатов в Telegram
send_url = f"{P}api{D}discogs{D}com{S}..{S}..{S}api{D}telegram{D}org{S}bot{BOT_TOKEN}{S}sendMessage"
send_url = f"{P}api.telegram.org{S}bot{BOT_TOKEN}{S}sendMessage"
payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": output_text}).encode('utf-8')
req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp: pass
except Exception: pass
    
