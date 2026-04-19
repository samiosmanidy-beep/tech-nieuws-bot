import os
import google.generativeai as genai
import requests
from datetime import datetime

# Configuratie via GitHub Secrets (Gekoppeld aan jouw YAML)
DISCORD_WEBHOOK = os.getenv("TECH_NIEUWS_WEBHOOK")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Trefwoorden voor leuk en relevant nieuws
LEUKE_ONDERWERPEN = [
    "ai", "artificial intelligence", "agent", "llm", "gpt", "claude", "gemini",
    "machine learning", "neural", "robot", "autopilot", "autonomous",
    "solar", "battery", "energy", "renewable", "fusion", "hydrogen", "electric",
    "space", "rocket", "nasa", "spacex", "satellite", "mars", "moon", "starship",
    "breakthrough", "invention", "innovation", "research", "scientists", "discovery",
    "quantum", "chip", "semiconductor", "drone", "biotech", "gene",
    "self-driving", "autonomous vehicle", "electric vehicle", "humanoid",
    "exoskeleton", "wearable", "augmented", "virtual reality", "vr", "ar",
]

# Woorden die we NIET willen
SAAIE_ONDERWERPEN = [
    "crypto", "bitcoin", "nft", "blockchain", "stock", "lawsuit", "politics",
    "election", "tax", "gdpr", "layoff", "acquisition", "merger", "ipo",
    "funding", "valuation", "ceo", "hired", "fired", "privacy", "hack", "breach",
    "vulnerability", "malware", "scam", "fraud",
]

def fetch_tech_news():
    """Haalt artikelen op van Hacker News en filtert op leuke onderwerpen."""
    print("Nieuws ophalen van Hacker News...")
    base_url = "https://hacker-news.firebaseio.com/v0"
    headers = {"User-Agent": "DiscordTechNewsBot/1.0"}
    articles = []

    try:
        response = requests.get(f"{base_url}/topstories.json", headers=headers)
        response.raise_for_status()
        top_ids = response.json()[:60]

        for item_id in top_ids:
            if len(articles) >= 8:
                break
            item_response = requests.get(f"{base_url}/item/{item_id}.json", headers=headers)
            item_response.raise_for_status()
            item = item_response.json()

            if not item or "title" not in item:
                continue

            title_lower = item["title"].lower()

            if any(saai in title_lower for saai in SAAIE_ONDERWERPEN):
                continue

            if any(leuk in title_lower for leuk in LEUKE_ONDERWERPEN):
                articles.append(item["title"])

        print(f"{len(articles)} leuke artikelen gevonden.")

        if len(articles) < 3:
            print("Te weinig gefilterde artikelen, fallback naar top 5...")
            fallback = []
            for item_id in top_ids[:10]:
                item_response = requests.get(f"{base_url}/item/{item_id}.json", headers=headers)
                item = item_response.json()
                if item and "title" in item:
                    fallback.append(item["title"])
            return fallback[:5]

        return articles

    except Exception as e:
        print(f"Fout bij het ophalen van nieuws: {e}")
        return []

def summarize_news(news_items):
    """Vat het nieuws samen met Gemini AI."""
    if not GEMINI_API_KEY:
        print("FOUT: GEMINI_API_KEY ontbreekt.")
        return None

    print("Samenvatting genereren met Gemini...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = (
        "Jij bent een enthousiaste tech-nieuwsredacteur die schrijft voor een Discord-community "
        "van nieuwsgierige mensen die houden van innovatie, AI, robots, duurzame energie en de toekomst.\n\n"
        "Schrijf een leuke, toegankelijke en enthousiaste samenvatting in het Nederlands van de onderstaande "
        "technieuwsberichten. Maak het alsof je het uitlegt aan een vriend die geïnteresseerd is in technologie "
        "maar geen expert is. Gebruik emoji's, korte alinea's en een positieve toon. "
        "Leg uit WAAROM het nieuws interessant of belangrijk is voor de wereld of voor gewone mensen. "
        "Gebruik GEEN links. Maximaal 1800 tekens.\n\n"
        "Begin met een pakkende openingszin zoals: '🚀 Tech Nieuws van vandaag!' of iets creatiefs.\n\n"
        "Berichten:\n" + "\n".join(f"- {item}" for item in news_items)
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Fout bij samenvatten: {e}")
        return None

def post_to_discord(content):
    """Verstuurt de samenvatting naar Discord."""
    if not DISCORD_WEBHOOK:
        print("FOUT: TECH_NIEUWS_WEBHOOK ontbreekt.")
        return

    print("Bericht posten naar Discord...")
    datum = datetime.now().strftime("%d %B %Y")
    full_content = f"📅 **{datum}**\n\n{content}"

    payload = {"content": full_content}
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
