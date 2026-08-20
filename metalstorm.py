import os
import urllib.request
import urllib.parse
import json

# Данные авторизации
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185
DISCOGS_TOKEN = "pMJGQnTxUPhrxUHCFytavDSnxAOiBwhPjjxuDtue"

# Защитные ASCII-переменные
S = chr(47); C = chr(58); Q = chr(63); A = chr(38); E = chr(61); D = chr(46)
P = "https" + C + S + S
D_API = "api" + D + "discogs" + D + "com" + S + "database" + S + "search"
TG_BASE = "api.telegram.org" + S + "bot"

# Намертво привязываем поиск к ИЮЛЮ 2026 года для этого теста
TARGET_STYLE = "Depressive Black Metal"
TARGET_YEAR = "2026"

print("📡 Запуск прямой разведки DSBM за ИЮЛЬ 2026...")

headers = {
    'User-Agent': 'MetalHubJulySpy/1.0',
    'Authorization': f'Discogs token={DISCOGS_TOKEN}'
}

encoded_style = urllib.parse.quote(TARGET_STYLE)

# Делаем прямой запрос. В Discogs API нельзя указать месяц в URL, поэтому выкачиваем весь 2026
url = f"{P}{D_API}{Q}style{E}{encoded_style}{A}year{E}{TARGET_YEAR}{A}type{E}release{A}format{E}album{A}per_page{E}100"

packs = []

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get("results", [])
            
            for item in results:
                title_raw = item.get("title", "")
                if not title_raw or " - " not in title_raw:
                    continue
                
                # Вытаскиваем точную дату, которую Discogs привязал к этой карточке
                # Она может лежать в поле 'released' или в блоке года
                full_date = item.get("released", "Дата отсутствует")
                country = item.get("country", "Unknown")
                
                # Нам интересны ТОЛЬКО те релизы, где в дате есть июльские маркеры ("-07-" или "2026-07")
                if "-07-" in full_date or "2026-07" in full_date:
                    release_info = f"💿 {title_raw}\n📅 Точная дата на Discogs: {full_date}\n🌍 Страна издания: {country}"
                    packs.append(release_info)
                    
except Exception as e:
    print(f"❌ Ошибка сбора данных: {e}")

# Сборка текста отчета
if packs:
    output_text = f"🎯 Найдено {len(packs)} июльских DSBM-карточек:\n\n" + "\n---\n".join(packs)
else:
    output_text = "🤷‍♂️ В сырой базе Discogs не найдено альбомов со строгой датой за 2026-07."

# Отправка в Telegram
send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": output_text}).encode('utf-8')
req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp: pass
except Exception: pass
    
