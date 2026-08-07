import urllib.request
import urllib.parse
import json

def fetch_bandcamp_final_api():
    print("🔥 Попытка прорыва через скрытый JSON-шлюз Bandcamp...")
    
    # Твоя оригинальная склейка URL без изменений
    url = P + W + "bandcamp.com" + S + "api" + S + "discover" + S + "3" + S + "get_web"
    
    # ИСПРАВЛЕНИЕ: Передаем тег строкой, а не списком!
    # API Bandcamp не принимает квадратные скобки [] для тега в этом шлюзе.
    payload = {
        "tag": "black-metal",
        "category": "album",
        "sort_key": "date",
        "page": 0
    }
    
    # ИСПРАВЛЕНИЕ: Добавляем обязательные заголовки Origin и Referer.
    # Без них защита Cloudflare на стороне Bandcamp сбрасывает запросы от urllib.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Content-Type': 'application/json',
        'Origin': "https" + C + S + S + "bandcamp.com",
        'Referer': "https" + C + S + S + "bandcamp.com" + S
    }
    
    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                return "❌ Сервер Bandcamp отклонил запрос плеера."
                
            data = json.loads(response.read().decode('utf-8'))
            
        results = data.get("items", [])
        if not results:
            return "🫙 На скрытой витрине Bandcamp сейчас пусто."
            
        packs = []
        for item in results[:7]: # Берем ровно 7 самых свежих альбомов
            band = item.get("artist_name", "Unknown Artist").strip()
            album = item.get("title", "Unknown Album").strip()
            album_url = item.get("url", "").strip()
            
            if not album_url: 
                continue
                
            # Чистим ссылку от хвостиков статистики
            clean_url = album_url.split('?')[0]
            
            # Твоя фирменная безопасная склейка текста для экрана телефона
            # Разрываем ссылку, чтобы она гарантированно не ломалась при копировании
            block = band + " - " + album + "\n🇳🇴 Black Metal\n" + clean_url
            packs.append(block)
            
        if packs:
            return "\n---\n".join(packs)
        return "Свежих релизов в пакете API не обнаружено."
        
    except Exception as e:
        return "❌ Ошибка прорыва через API: " + str(e)
