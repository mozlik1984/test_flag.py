import os
import urllib.request
import urllib.parse
import json
import time
import sys

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5002053185

S = chr(47); C = chr(58); Q = chr(63); E = chr(61)
P = "https" + C + S + S

COUNTRY_TO_FLAG = {
    "Norway": "🇳🇴", "Sweden": "🇸🇪", "Finland": "🇫🇮", "Germany": "🇩🇪",
    "France": "🇫🇷", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "Ukraine": "🇺🇦", "Russia": "🇷🇺", "Austria": "🇦🇹", "Iceland": "🇮🇸",
    "Poland": "🇵🇱", "Greece": "🇬🇷", "Italy": "🇮🇹", "Switzerland": "🇨🇭",
    "Netherlands": "🇳🇱", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Spain": "🇪🇸",
    "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷", "Japan": "🇯🇵",
    "Wales": "🏴󠁧󠁢🇺󠁬󠁳󠁿", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰", 
    "Indonesia": "🇮🇩", "Hungary": "🇭🇺", "Ireland": "🇮🇪", "Colombia": "🇨🇴",
    "Chile": "🇨🇱", "Argentina": "🇦🇷", "Mexico": "🇲🇽", "New Zealand": "🇳🇿",
    "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Estonia": "🇪🇪"
}

COUNTRY_MAP = {
    "NO": "Norway", "SE": "Sweden", "FI": "Finland", "DE": "Germany", 
    "FR": "France", "US": "United States", "GB": "United Kingdom", 
    "UA": "Ukraine", "RU": "Russia", "AT": "Austria", "IS": "Iceland", 
    "PL": "Poland", "GR": "Greece", "IT": "Italy", "CH": "Switzerland", 
    "NL": "Netherlands", "AU": "Australia", "CA": "Canada", "BR": "Brazil", 
    "JP": "Japan", "CZ": "Czech Republic", "DK": "Denmark", "ID": "Indonesia", 
    "HU": "Hungary", "IE": "Ireland", "CO": "Colombia", "CL": "Chile", 
    "AR": "Argentina", "MX": "Mexico", "NZ": "New Zealand", "SK": "Slovakia", 
    "SI": "Slovenia", "EE": "Estonia"
}

def fetch_musicbrainz_new_arrivals():
    months_map = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    months_num_map = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    
    time_struct = time.gmtime()
    current_month_tag = months_map.get(time_struct.tm_mon, "JUL")
    current_month_num = str(time_struct.tm_mon).zfill(2)
    current_year = time_struct.tm_year
    user_corrections = ""
    
    if len(sys.argv) > 2:
        input_month = str(sys.argv[1]).strip().upper()
        input_year = str(sys.argv[2]).strip()
        if len(sys.argv) > 3: user_corrections = str(sys.argv[3]).strip()
        
        if input_month != "AUTO" and input_month in months_num_map:
            current_month_tag = input_month
            current_month_num = months_num_map[input_month]
        if input_year != "AUTO" and input_year.isdigit():
            current_year = int(input_year)

    print(f"🛰️ Поиск релизов за цель: {current_month_tag} {current_year}")
    
    query = f'type:album AND status:official AND date:{current_year} AND (tag:"black metal" OR tag:"*black metal*" OR tag:"blackened *" OR tag:"dsbm" OR tag:"blackgaze" OR tag:"war metal")'
    url = P + "musicbrainz.org" + S + "ws" + S + "2" + S + "release" + "?query=" + urllib.parse.quote(query) + "&inc=tags+artist-credits&fmt=json&limit=100"
    headers = {'User-Agent': 'BlackMetalHubBot/17.0 ( mailto:Plokhomentov@example.com )'}
    
    try:
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        break
            except urllib.error.HTTPError as he:
                if he.code == 503 and attempt < 2:
                    time.sleep(3)
                    continue
                raise he
        else:
            return "❌ Сервер MusicBrainz перегружен (503). Попробуйте запустить позже."

        releases = data.get("releases", [])
        packs = []
        seen_albums = set()
        
        for rel in releases:
            rel_date = rel.get("date", "")
            if rel_date:
                date_parts = rel_date.split("-")
                if len(date_parts) > 1:
                    if date_parts[1] != current_month_num:
                        continue

            artist_credit = rel.get("artist-credit", [])
            if not artist_credit: continue
            
            first_artist = artist_credit[0] if isinstance(artist_credit, list) else artist_credit
            artist_data = first_artist.get("artist", {})
            band = artist_data.get("name", "").strip()
            album = rel.get("title", "").strip()
            artist_id = artist_data.get("id", "")
            
            if band and album:
                release_key = band.lower() + " - " + album.lower()
                if release_key in seen_albums: continue
                seen_albums.add(release_key)
                
                tags_list = [t.get("name", "").lower() for t in rel.get("tags", [])]
                tags_str = " ".join(tags_list)
                
                subgenres = []
