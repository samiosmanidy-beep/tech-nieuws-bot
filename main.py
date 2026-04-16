import os
import requests
import google.generativeai as genai

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def fetch_tech_news():
        urls = [
                    "https://www.reddit.com/r/technology/top.json?limit=6&t=day",
                    "https://www.reddit.com/r/gadgets/top.json?limit=4&t=day"
        ]

    headers = {"User-Agent": "DiscordTechNewsBot/1.0"}
    articles = []

    for url in urls:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                                data = response.json()
                                posts = data.get('data', {}).get('children', [])
                                for post in posts:
                                                    title = post.get('data', {}).get('title', '')
                                                    articles.append(f"- {title}")

    return articles

def summarize_with_gemini(articles):
        model = genai.GenerativeModel('gemini-1.5-flash') 

    news_list = "\n".join(articles)

    prompt = (
                "Je bent een vriendelijke tech-nieuwslezer voor een Discord-kanaal. "
                "Ik geef je een lijst met recente tech-nieuwtjes. "
                "Kies de 4 a 5 meest interessante en 'algemene' tech-onderwerpen uit "
                "(zoals nieuwe gadgets, robots, auto's, zonne-energie, AI of AR) "
                "en schrijf hier een boeiende en feitelijke samenvatting van in vloeiend Nederlands.\n\n"
                "Regels waaraan je MOET voldoen:\n"
                "- Gebruik GEEN URL's of linkjes in je bericht.\n"
                "- Maak er een leuk, samenhangend verhaal van met eventueel een paar gepaste emoji's.\n"
                "- Vermeld geen bronnen of namen van de auteurs.\n\n"
                f"Hier zijn de ruwe titels van vandaag:\n\n{news_list}"
    )

    response = model.generate_content(prompt)
    return response.text.strip()

def post_to_discord(content):
        data = {"content": content, "username": "Daily Tech Flash"}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print("Nieuws succesvol naar Discord gestuurd!")

if __name__ == "__main__":
        if not DISCORD_WEBHOOK_URL or not GEMINI_API_KEY:
                    print("FOUT: DISCORD_WEBHOOK_URL en/of GEMINI_API_KEY missen!")
                    exit(1)
                news_items = fetch_tech_news()
    if not news_items: exit(1)
            summary = summarize_with_gemini(news_items)
    post_to_discord(summary)
