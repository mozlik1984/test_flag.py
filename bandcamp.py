import os
import re
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import telebot
from apscheduler.schedulers.background import BackgroundScheduler

# Конфигурация (замените на свои данные или настройте переменные окружения)
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "ВАШ_ТОКЕН_БОТА")
ADMIN_CHAT_ID = 5002053185  # Ваш ID из скриншота

bot = telebot.TeleBot(BOT_TOKEN)

# Список целевых поджанров Блэк-метала на Bandcamp
BLACK_METAL_TAGS = [
    "black-metal", "atmospheric-black-metal", "depressive-black-metal", 
    "raw-black-metal", "symphonic-black-metal", "post-black-metal", 
    "melodic-black-metal", "blackgaze"
]

# Запрещенные теги (если они есть в релизе — пропускаем его)
FORBIDDEN_TAGS = ["thrash-metal", "death-metal", "heavy-metal", "power-metal", "metalcore"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_bandcamp_by_date(target_month=None, target_year=None):
    """
    Основная функция парсинга.
    Если target_month и target_year не заданы — собирает релизы за ТЕКУЩИЙ месяц.
    Если заданы (например, month=12, year=2022) — ищет релизы за тот период.
    """
    now = datetime.now()
    req_month = target_month if target_month else now.month
    req_year = target_year if target_year else now.year
    
    found_releases = []
    seen_urls = set() # Чтобы избежать дубликатов из разных тегов

    print(f"Поиск блэк-метала за период: {req_month}/{req_year}...")

    # Проходим по всем трушным блэк-метал тегам
    for tag in BLACK_METAL_TAGS:
        url = f"https://bandcamp.com{tag}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, "html.parser")
            pagedata_tag = soup.find("div", id="pagedata") or soup.find("script", {"id": "pagedata"})
            if not pagedata_tag:
                continue
                
            data = json.loads(pagedata_tag.get("data-blob") or pagedata_tag.text)
            dig_deeper = data.get("hub_data", {}).get("tabs", {}).get("dig_deeper", {}).get("initial_results", [])
            
            for item in dig_deeper:
                album_url = item.get("tralbum_url")
                if not album_url or album_url in seen_urls:
                    continue
                    
                # Жесткая фильтрация жанров (проверка на чистоту блэка)
                item_tags = [t.lower() for t in item.get("tags", [])]
                if any(forbidden in item_tags for forbidden in FORBIDDEN_TAGS):
                    continue # Скипаем чистый трэш/дэт
                
                # Проверка даты релиза (Bandcamp отдает ее в разных форматах, парсим базово)
                # Примечание: для глубокого анализа старых периодов здесь настраивается пагинация (page++)
                rel_date_str = item.get("release_date") # Обычно строковый формат вроде "01 Aug 2026"
                if rel_date_str:
                    try:
                        # Пример парсинга: "05 Aug 2026" -> объект datetime
                        rel_date = datetime.strptime(rel_date_str, "%d %b %Y")
                        if rel_date.month == req_month and rel_date.year == req_year:
                            album_data = {
                                "artist": item.get("artist"),
                                "title": item.get("title"),
                                "url": album_url.split('?')[0] # Чистим ссылку от реферальных хвостов
                            }
                            found_releases.append(album_data)
                            seen_urls.add(album_url)
                    except Exception:
                        # Если формат даты специфичный, берем в текущий фид на всякий случай
                        if not target_month: 
                            album_data = {
                                "artist": item.get("artist"),
                                "title": item.get("title"),
                                "url": album_url.split('?')[0]
                            }
                            found_releases.append(album_data)
                            seen_urls.add(album_url)

        except Exception as e:
            print(f"Ошибка при обработке тега {tag}: {e}")
            continue
            
    return found_releases[:10] # Ограничим 10 релизами для одного сообщения

def format_and_send(releases, title_text, chat_id):
    """Форматирует результат в красивое сообщение для отправки в Telegram"""
    if not releases:
        bot.send_message(chat_id, f"<b>{title_text}</b>\n\nНовых релизов не обнаружено.", parse_mode="HTML")
        return

    msg = f"<b>{title_text}</b>\n\n"
    for r in releases:
        msg += f"• <code>{r['artist']} - {r['title']}</code>\n🔗 {r['url']}\n\n"
        
    bot.send_message(chat_id, msg, parse_mode="HTML", disable_web_page_preview=True)

# --- БЛОК АВТОМАТИЗАЦИИ (ПО ПОНЕДЕЛЬНИКАМ) ---
def weekly_auto_job():
    now = datetime.now()
    months_ru = {1:"Январь", 2:"Февраль", 3:"Март", 4:"Апрель", 5:"Май", 6:"Июнь", 7:"Июль", 8:"Август", 9:"Сентябрь", 10:"Октябрь", 11:"Ноябрь", 12:"Декабрь"}
    title = f"🇳🇴 ЕЖЕНЕДЕЛЬНЫЙ БЛЭК-МЕТАЛ УЛОВ ({months_ru[now.month]} {now.year})"
    
    releases = parse_bandcamp_by_date() # Ищет за текущий месяц/год
    format_and_send(releases, title, ADMIN_CHAT_ID)

# Настройка планировщика (запуск каждый понедельник в 10:00)
scheduler = BackgroundScheduler()
scheduler.add_job(weekly_auto_job, 'cron', day_of_week='mon', hour=10, minute=0)
scheduler.start()


# --- БЛОК РУЧНОГО ЗАПРОСА (ИНТЕРФЕЙС БОТА) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я автономный Блэк-метал парсер.\n"
                          "Каждый понедельник я присылаю свежак.\n\n"
                          "Чтобы запросить архив, введи команду в формате:\n"
                          "<code>/archive ММ.ГГГГ</code> (например: <code>/archive 12.2022</code>)", parse_mode="HTML")

@bot.message_handler(commands=['archive'])
def get_archive_data(message):
    try:
        # Извлекаем дату из команды /archive 12.2022
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Укажите дату! Пример: `/archive 12.2022`", parse_mode="Markdown")
            return
            
        date_part = args[1]
        match = re.match(r"(\d{2})\.(\d{4})", date_part)
        if not match:
            bot.reply_to(message, "Неверный формат. Используйте ММ.ГГГГ (например, 09.2025)")
            return
            
        month = int(match.group(1))
        year = int(match.group(2))
        
        bot.send_message(message.chat.id, f"⏳ Начинаю раскопки архивов за {month}.{year}...")
        
        releases = parse_bandcamp_by_date(target_month=month, target_year=year)
        title = f"🏛 АРХИВНЫЙ УЛОВ ЗА {month}.{year} (Strict Black Metal)"
        
        format_and_send(releases, title, message.chat.id)
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обработке запроса: {e}")

if __name__ == "__main__":
    print("Бот успешно запущен и ждет понедельников...")
    bot.infinity_polling()
    
