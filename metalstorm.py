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

# Инициализация календаря и периодов поиска
months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
months_num_map = {"JUL": "07", "AUG": "08", "SEP": "09"}

# Динамическое считывание аргументов ручного запуска (GitHub Actions)
# sys.argv[0] - имя скрипта, sys.argv[1] - месяц, sys.argv[2] - год
if len(sys.argv) > 1:
    current_month_tag = str(sys.argv[1]).strip().upper()
else:
    current_month_tag = "AUG" # Дефолт, если запуск пустой

if len(sys.argv) > 2:
    current_year = str(sys.argv[2]).strip().upper()
else:
    current_year = "2026"

# Если в Гитхабе выбрано "AUTO", подставляем текущий системный месяц
if current_month_tag == "AUTO" or current_month_tag not in months_num_map:
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "AUG")

if current_year == "AUTO":
    time_struct = time.gmtime()
    current_year = str(time_struct.tm_year)

# Формируем жесткий строковый маркер месяца для фильтрации Discogs (например, "-07-")
target_month_marker = f"-{months_num_map[current_month_tag]}-"

print(f"📡 Скрипт успешно принял аргументы Гитхаба!")
print(f"📅 Целевой период поиска: {current_month_tag} {current_year} (Маркер: {target_month_marker})")

# Сборка авторизационных заголовков с персональным токеном
headers = {
    'User-Agent': 'MetalHubDSBMCalibrator/3.0',
    'Authorization': f'Discogs token={DISCOGS_TOKEN}'
}

# Массивы хранения уникальных данных
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
                
                if "(" in band and ")" in band:
                    continue
                    
                # --- УЛЬТИМАТИВНЫЙ КАЛЕНДАРНЫЙ ФИЛЬТР ---
                # Вытягиваем точную строковую дату релиза (поле 'released_date' или 'year')
                # Нам нужны только релизы, содержащие маркер выбранного месяца (например, "2026-08")
                full_date = item.get("released", "") # Discogs отдает дату как YYYY-MM-DD в поисковой выдаче
                
                if full_date:
                    # Если ищем август, а дата 2026-03-22 (как у Aurora Disease) — скипаем!
                    if target_month_marker not in full_date and not full_date.endswith(months_num_map[current_month_tag]):
                        continue
                else:
                    # Если точной даты месяца вообще нет в базе — скипаем для стерильности
                    continue
                
                release_key = f"{band.lower()} - {album.lower()}"
                if release_key in seen_releases:
                    continue
                seen_releases.add(release_key)
                
                release_info = f"{band} - {album} ({current_year})\n💀 {TARGET_STYLE}\n{P}{YT_BASE} {current_month_tag}"
                packs.append(release_info)
except Exception as e:
    print(f"❌ Ошибка калибровки: {e}")

# Отправка стерильного чанка
output_text = "\n---\n".join(packs) if packs else f"За {current_month_tag} {current_year} новых DSBM альбомов не обнаружено."
send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": output_text}).encode('utf-8')
req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp: pass
except Exception: pass
    
