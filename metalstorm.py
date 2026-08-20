import os
import urllib.request
import json

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58); Q = chr(63); E = chr(61); D = chr(46)
P = "https" + C + S + S
TG_BASE = "api.telegram.org" + S + "bot"

# Для теста берем открытый структурированный музыкальный лог-канал
TARGET_CHANNEL = "metalprogression"
final_url = f"{P}t{D}me{S}s{S}{TARGET_CHANNEL}"

print(f"📡 Запуск теста v14.1: Изучаем структуру анкетных постов...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

packs = []

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            html = response.read().decode('utf-8', errors='ignore')
            
            marker = 'class="tgme_widget_message_text'
            pos = 0
            while True:
                idx = html.find(marker, pos)
                if idx == -1: break
                
                start_text = html.find('>', idx) + 1
                end_text = html.find('</div>', start_text)
                if end_text == -1: break
                
                raw_text = html[start_text:end_text]
                pos = end_text
                
                # Очищаем HTML-теги, сохраняя переносы строк
                clean_text = raw_text.replace('<br/>', '\n').replace('<br>', '\n')
                while True:
                    s_idx = clean_text.find('<')
                    if s_idx == -1: break
                    e_idx = clean_text.find('>', s_idx)
                    if e_idx == -1: break
                    clean_text = clean_text[:s_idx] + clean_text[e_idx+1:]
                
                lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
                if lines and len(lines) > 2:
                    # Забираем первые 4 строки анкеты для изучения
                    packs.append(f"📋 Анкета сообщения:\n" + "\n".join(lines[:4]))
                    
except Exception as e:
    print(f"❌ Ошибка: {e}")

output_text = "\n---\n".join(packs[:4]) if packs else "Посты со структурой не найдены."
send_url = f"{P}{TG_BASE}{BOT_TOKEN}{S}sendMessage"
payload = json.dumps({"chat_id": ADMIN_CHAT_ID, "text": output_text}).encode('utf-8')
req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as resp: pass
except Exception: pass
    
