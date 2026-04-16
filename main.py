import os
import google.generativeai as genai
import requests
import json
from datetime import datetime

# Configuratie via GitHub Secrets (Environment Variables)
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def fetch_tech_news():
    """Haalt de top 5 artikelen op van Hacker News."""
    print("Nieuws ophalen van Hacker News...")
    urls = [
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        "https://hacker-news.firebaseio.com/v0/item/{}.json"
    ]
    headers = {"User-Agent": "DiscordTechNewsBot/1.0"}
    articles = []

    try:
        response = requests.get(urls[0], headers=headers)
        response.raise_for_status()
        top_ids = response.json()[:5]

        for item_id in top_ids:
            item_response = requests.get(urls[1].format(item_id), headers=headers)
            item_response.raise_for_status()
            item_data = item_response.json()
            if "title" in item_data:
                articles.append(item_data["title"])
        
        print(f"{len(articles)} artikelen gevonden.")
        return articles
    except Exception as e:
        print(f"Fout bij het ophalen van nieuws: {e}")
        return []

def summarize_news(news_items):
    """Vat de nieuwsberichten samen met Gemini AI in het Nederlands."""
    if not GEMINI_API_KEY:
        print("FOUT: GEMINI_API_KEY ontbreekt in de environment.")
        return None

    print("Samenvatting genereren met Gemini...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = (
        "Vat de volgende 5 technieuws berichten van Hacker News samen in een kort, "
        "feitelijk Nederlands rapport voor Discord. Gebruik maximaal 2000 tekens. "
        "Gebruik GEEN links. Toon alleen de belangrijkste feiten.\n\n"
        "Berichten:\n" + "\n".join(f"- {item}" for item in news_items)
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Fout bij het samenvatten: {e}")
        return None

def post_to_discord(content):
    """Verstuurt de samenvatting naar Discord."""
    if not DISCORD_WEBHOOK:
        print("FOUT: DISCORD_WEBHOOK ontbreekt in de environment.")
        return

    print("Bericht posten naar Discord...")
    payload = {"content": content}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        response.raise_for_status()
        print("Succesvol gepost naar Discord!")
    except Exception as e:
        print(f"Fout bij posten naar Discord: {e}")

if __name__ == "__main__":
    news_items = fetch_tech_news()
    
    if not news_items:
        print("Geen nieuws gevonden. Script stopt.")
        exit(1)
    
    summary = summarize_news(news_items)
    
    if summary:
        post_to_discord(summary)
    else:
        print("Geen samenvatting gegenereerd.")
