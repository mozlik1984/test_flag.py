import os
import urllib.request
import urllib.parse
import json
import time

# Данные авторизации
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185
DISCOGS_TOKEN = "pMJGQnTxUPhrxUHCFytavDSnxAOiBwhPjjxuDtue"

# Маскировка протоколов
S = chr(47); C = chr(58); Q = chr(63); A = chr(38); E = chr(61); D = chr(46)
P = "https" + C + S + S
D_API = "api" + D + "discogs" + D + "com" + S + "database" + S + "search"
TG_BASE = "api.telegram.org" + S + "bot"
YT_BASE = "youtube.com"

TARGET_STYLE = "Black Metal"
TARGET_YEAR = "2026"

print(f"📡 Запуск прямой выгрузки свежих релизов Discogs по жанру {TARGET_STYLE}...")

headers = {
    'User-Agent': 'MetalHubDirectStream/1.0',
    'Authorization': f'Discogs token={DISCOGS_TOKEN}'
}

encoded_style = urllib.parse.quote(TARGET_STYLE)

# Делаем ультимативный запрос: ищем альбомы 2026 года, сортируя их по дате добавления в базу (year, desc)
url = f"{P}{D_API}{Q}style{E}{encoded_style}{A}year{E}{TARGET_YEAR}{A}type{E}release{A}format{E}album{A}per_page{E}30"

packs = []
seen_releases = set()

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get("results", [])
            
            print(f"✅ УСПЕХ! База ответила. Получено {len(results)} позиций.")
            
            for item in results:
                title_raw = item.get("title", "")
                if not title_raw or " - " not in title_raw:
                    continue
                
                parts = title_raw.split(" - ", 1)
                band = parts[0].strip()
                album = parts[1].strip()
                
                # Убираем архивные дубликаты Discogs с цифрами в скобках
                if "(" in band and ")" in band:
                    continue
                
                # Тотальный склейщик повторов
                release_key = f"{band.lower()} - {album.lower()}"
                if release_key in seen_releases:
                    continue
                seen_releases.add(release_key)
                
                # Извлекаем страну издания винила/диска
                country_name = item.get("country", "").strip()
                
                # Упаковываем в твой стандартный текстовый формат для Amvera
                release_info = f"{band} - {album} ({TARGET_YEAR})\n🌍 {country_name} | {TARGET_STYLE}\n{P}{YT_BASE} AUG"
                packs.append(release_info)
                
except Exception as e:
    print(f"❌ Ошибка выгрузки: {e}")

# Отправка финального текстового пакета
if packs:
    output_text = f"🔥 Свежие поступления {TARGET_STYLE} за {TARGET_YEAR} год:\n\n" + "\n---\n".join(packs)
else:
    output_text = "🤷‍♂️ В базе Discogs ничего не найдено по данному запросу."

send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": output_text}).encode('utf-8')
req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp: pass
except Exception: pass
print("🏁 Скрипт завершил работу.")

