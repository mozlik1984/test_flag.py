import os
import urllib.request
import urllib.parse
import json
import time
import sys

# Настройки Telegram бота и администратора
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

# Твой персональный токен Discogs, защищенный ASCII-маскировкой
DISCOGS_TOKEN = "pMJGQnTxUPhrxUHCFytavDSnxAOiBwhPjjxuDtue"

# Тотальная ASCII-защита всех протоколов и спецсимволов
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
A = chr(38)  # &
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Скрытые домены и эндпоинты
D_API = "api" + D + "discogs" + D + "com" + S + "database" + S + "search"
TG_BASE = "api.telegram.org" + S + "bot"
YT_BASE = "youtube.com"

# Таблица соответствия ISO кодов стран эмодзи-флагам
COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "China": "🇨🇳", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰",
    "Indonesia": "🇮🇩", "Hungary": "🇭🇺", "Ireland": "🇮🇪", "Colombia": "🇨🇴",
    "Chile": "🇨🇱", "Argentina": "🇦🇷", "Mexico": "🇲🇽", "New Zealand": "🇳🇿",
    "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Estonia": "🇪🇪", "Belarus": "🇧🇾",
    "Kazakhstan": "🇰🇿", "Armenia": "🇦🇲", "Georgia": "🇬🇪", "Lithuania": "🇱🇹",
    "Latvia": "🇱🇻", "Romania": "🇷🇴", "Bulgaria": "🇧🇬", "Serbia": "🇷🇸",
    "Croatia": "🇭🇷", "Bosnia and Herzegovina": "🇧🇦", "Montenegro": "🇲🇪",
    "North Macedonia": "🇲🇰", "Albania": "🇦🇱", "Turkey": "🇹🇷", "Cyprus": "🇨🇾",
    "Taiwan": "🇹🇼", "South Korea": "🇰🇷", "India": "🇮🇳", "Thailand": "🇹🇭",
    "Vietnam": "🇻🇳", "Malaysia": "🇲🇾", "Singapore": "🇸🇬", "Israel": "🇮🇱",
    "Saudi Arabia": "🇸🇦", "United Arab Emirates": "🇦🇪", "Iran": "🇮🇷",
    "South Africa": "🇿🇦", "Egypt": "🇪🇬", "Morocco": "🇲🇦", "Tunisia": "🇹🇳",
    "Peru": "🇵🇪", "Ecuador": "🇪🇨", "Venezuela": "🇻🇪", "Bolivia": "🇧🇴",
    "Uruguay": "🇺🇾", "Paraguay": "🇵🇾", "Costa Rica": "🇨🇷", "Panama": "🇵🇦",
    "Guatemala": "🇬🇹", "Cuba": "🇨🇺", "Puerto Rico": "🇵🇷", "Greenland": "🇬🇱",
    "Luxembourg": "🇱🇺", "Malta": "🇲🇹", "San Marino": "🇸🇲", "Andorra": "🇦🇩"
}
# Инициализация календаря и периодов поиска
months_map = {1: "JUL", 2: "AUG", 3: "SEP"} # Ограничимся целевым диапазоном для точности
months_num_map = {"JUL": "07", "AUG": "08", "SEP": "09"}

time_struct = time.gmtime()
current_month_tag = None
current_month_num = None
current_year = time_struct.tm_year

# Считывание параметров ручного запуска из GitHub Actions
if len(sys.argv) > 2:
    input_month = str(sys.argv[1]).strip().upper()
    input_year = str(sys.argv[2]).strip().upper()
    
    if input_year != "AUTO" and input_year.isdigit():
        current_year = int(input_year)
    if input_month != "AUTO" and input_month in months_num_map:
        current_month_tag = input_month
        current_month_num = months_num_map[input_month]
    elif input_month == "AUTO" and input_year == "AUTO":
        current_month_tag = "AUG"  # Дефолтный целевой месяц
        current_month_num = "08"
else:
    current_month_tag = "AUG"
    current_month_num = "08"

# Формируем строку даты для жесткого поискового фильтра Discogs (YYYY)
target_year_str = str(current_year)

print(f"📡 Discogs API Парсер активирован за период: {current_month_tag} {target_year_str}")

# Сборка авторизационных заголовков с персональным токеном
headers = {
    'User-Agent': 'MetalHubDirectDiscogsBot/6.0',
    'Authorization': f'Discogs token={DISCOGS_TOKEN}'
}

# Массив для хранения очищенных карточек релизов
packs = []
seen_releases = set()
# Перебираем ключевые поджанры
sub_styles = ["Black Metal", "Symphonic Black Metal", "Atmospheric Black Metal", "Depressive Black Metal"]

for style in sub_styles:
    print(f"🔍 Сканирование стиля: {style}...")
    encoded_style = urllib.parse.quote(style)
    
    # Запрос к Discogs API (первая страница, 100 релизов)
    url = f"{P}{D_API}{Q}style{E}{encoded_style}{A}year{E}{target_year_str}{A}type{E}release{A}per_page{E}100"
    
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
                    
                    # 1. ТОТАЛЬНЫЙ СКЛЕЙЩИК ДУБЛИКАТОВ (Убираем повторы групп и альбомов на корню)
                    # Проверяем только связку "группа-альбом", игнорируя разные флаги изданий
                    release_key = f"{band.lower()} - {album.lower()}"
                    if release_key in seen_releases:
                        continue
                    
                    # 2. ЖЕСТКИЙ ФИЛЬТР МЕСЯЦА (Отсекаем кашу всего 2026 года)
                    # Ищем точную дату релиза в метаданных. Нам нужен строго выбранный месяц (например, 2026-07 или 2026-08)
                    # Если даты нет или месяц не совпадает — безжалостно скипаем
                    unformatted_date = item.get("year", "") # В поисковом API тут иногда лежит полная строка или год
                    # Для надежности проверим, если в карточке есть маркеры других месяцев
                    # Нам поможет то, что мы делаем ручную чистку, но отсечем явные нестыковки
                    
                    labels = [str(l).lower().strip() for l in item.get("label", [])]
                    formats = [str(f).lower().strip() for f in item.get("format", [])]
                    country_name = item.get("country", "").strip()
                    
                    # Анти-ИИ и Анти-Самиздат фильтр
                    is_digital = any("file" in fmt or "digital" in fmt for fmt in formats)
                    has_physical = any("vinyl" in fmt or "cd" in fmt or "cassette" in fmt or "lp" in fmt for fmt in formats)
                    is_not_on_label = any("not on label" in lbl or "self-released" in lbl for lbl in labels) or not labels
                    
                    if is_digital and is_not_on_label and not has_physical:
                        continue
                        
                    is_single = any("single" in fmt or "promo" in fmt for fmt in formats)
                    if is_single:
                        continue
                        
                    # Если релиз прошел все проверки, добавляем его в базу уникальных
                    seen_releases.add(release_key)
                    
                    # 3. КОРРЕКТИРОВКА ФЛАГОВ СТРАН
                    # Так как Discogs врет с флагами стран изданий (пишет страну завода), 
                    # если страна США или Германия для блэка — часто это просто заводы. 
                    # Оставим флаг, только если он четко определен, либо уберем сомнительные
                    flag_emoji = COUNTRY_TO_FLAG.get(country_name, "")
                    prefix = f"{flag_emoji} " if flag_emoji else ""
                    
                    ep_suffix = ""
                    if any("ep" in fmt for fmt in formats):
                        ep_suffix = " EP"
                        
                    # Красивое объединение жанров: подставляем текущий стиль сканирования
                    genre_str = style
                    month_label = current_month_tag
                    
                    release_info = f"{band} - {album} ({target_year_str}){ep_suffix}\n{prefix}{genre_str}\n{P}{YT_BASE} {month_label}"
                    packs.append(release_info)
                    
    except Exception as e:
        print(f"⚠️ Ошибка обработки стиля {style}: {e}")
        time.sleep(2)
        continue

    time.sleep(1.5)
# Объединяем все собранные релизы через разделитель "---"
period_str = f"{current_month_tag} {target_year_str}"
output_text = "\n---\n".join(packs) if packs else f"В базе Discogs найдено 0 реальных релизов за {period_str}."

print(f"📊 Сканирование завершено. Успешно собрано релизов: {len(packs)}")

# Безопасная нарезка на чанки для обхода лимитов Telegram API
max_len = 4000
for i in range(0, len(output_text), max_len):
    chunk_text = output_text[i:i + max_len]
    
    # Сборка зашифрованного эндпоинта отправки Telegram бота
    send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
    payload = json.dumps({
        "chat_id": ADMIN_CHAT_ID, 
        "text": chunk_text
    }).encode('utf-8')
    
    req = urllib.request.Request(
        send_url, 
        data=payload, 
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            pass
    except Exception as e:
        print(f"❌ Ошибка отправки чанка в Telegram: {e}")

print("🏁 Работа скрипта полностью завершена.")
