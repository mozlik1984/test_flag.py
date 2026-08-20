import os
import urllib.request
import urllib.parse
import json
import time
import sys

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185
DISCOGS_TOKEN = "pMJGQnTxUPhrxUHCFytavDSnxAOiBwhPjjxuDtue"

S = chr(47); C = chr(58); Q = chr(63); A = chr(38); E = chr(61); D = chr(46)
P = "https" + C + S + S
D_API = "api" + D + "discogs" + D + "com" + S + "database" + S + "search"
TG_BASE = "api.telegram.org" + S + "bot"
YT_BASE = "youtube.com"

# Берем строго один тестовый поджанр
TARGET_STYLE = "Depressive Black Metal"
TARGET_YEAR = "2026"

print(f"📡 Запуск точечной DSBM-разведки...")

headers = {
    'User-Agent': 'MetalHubDSBMDebug/1.0',
    'Authorization': f'Discogs token={DISCOGS_TOKEN}'
}

encoded_style = urllib.parse.quote(TARGET_STYLE)

# В ультимативный запрос добавляем format=album, чтобы отсечь мусорные переиздания синглов
url = f"{P}{D_API}{Q}style{E}{encoded_style}{A}year{E}{TARGET_YEAR}{A}type{E}release{A}format{E}album{A}per_page{E}50"

packs = []
seen_releases = set()

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
                    
                parts = title_raw.split(" - ", 1)
                band = parts[0].strip()
                album = parts[1].strip()
                
                # Защита от старых архивных переизданий (убираем скобки у банд)
                if "(" in band and ")" in band:
                    continue
                    
                release_key = f"{band.lower()} - {album.lower()}"
                if release_key in seen_releases:
                    continue
                seen_releases.add(release_key)
                
                formats = [str(f).lower() for f in item.get("format", [])]
                
                # Строго убираем синглы и промо, если они затесались
                if "single" in formats or "promo" in formats:
                    continue
                    
                # Формируем компактную карточку
                release_info = f"{band} - {album} ({TARGET_YEAR})\n💀 {TARGET_STYLE}\n{P}{YT_BASE} AUG"
                packs.append(release_info)
except Exception as e:
    print(f"❌ Ошибка теста: {e}")

# Отправка тестового чанка
output_text = "\n---\n".join(packs) if packs else "В тесте DSBM найдено 0 релизов."
send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": output_text}).encode('utf-8')
req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp: pass
except Exception: pass
    
