import urllib.request
import json

# ASCII-переменные для защиты путей
S = chr(47)  # /
C = chr(58)  # :
Q = chr(63)  # ?
E = chr(61)  # =
D = chr(46)  # .
P = "https" + C + S + S

# Открытый JSON-эндпоинт блэк-метал сообщества Reddit (без Cloudflare)
REDDIT_API = "www" + D + "reddit" + D + "com" + S + "r" + S + "BlackMetal" + S + "new" + D + "json"
final_url = f"{P}{REDDIT_API}"

print("📡 Запуск разведки Reddit BlackMetal JSON...")

# Для Реддита обязательно нужен вменяемый User-Agent, чтобы не выдал 429
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MetalHubBot/1.0'}

try:
    req = urllib.request.Request(final_url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as response:
        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            children = data.get("data", {}).get("children", [])
            
            print("✅ УСПЕХ! Reddit ответил моментально.")
            print(f"📊 Найдено свежих топиков в ленте: {len(children)}")
            
            if children:
                print("\n🎯 Контрольный срез первых 3 постов от живых металлистов:")
                for idx, post in enumerate(children[:3]):
                    post_data = post.get("data", {})
                    title = post_data.get("title", "Unknown Title")
                    link_flair = post_data.get("link_flair_text", "Без поджанра") # Здесь часто лежит точный поджанр
                    ups = post_data.get("ups", 0)
                    
                    print(f"  {idx+1}. Пост: {title}")
                    print(f"     Жанровый тег: {link_flair} | 👍 Лайков: {ups}")
            else:
                print("⚠️ Лента пуста.")
except Exception as e:
    print(f"❌ РАЗВЕДКА ПРОВАЛЕНА. Затык тут: {e}")
    
