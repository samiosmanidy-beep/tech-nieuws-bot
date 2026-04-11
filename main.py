import os
import requests
import google.generativeai as genai

def get_top_stories():
        try:
                    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
                    response = requests.get(top_stories_url)
                    response.raise_for_status()
                    story_ids = response.json()[:5]
                    stories = []
                    for story_id in story_ids:
                                    story_res = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
                                    if story_res.status_code == 200:
                                                        story_data = story_res.json()
                                                        if story_data and "title" in story_data:
                                                                                stories.append(story_data["title"])
                                                                    return stories
        except Exception as e:
                    print(f"Fout: {e}")
                    return []

    def summarize_with_ai(stories):
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                        return "GEMINI_API_KEY niet gevonden"
                    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    totaal_nieuws = "\n".join([f"- {title}" for title in stories])
    prompt = f'''
    Je krijgt hier de top 5 actuele koppen uit de tech-wereld (HackerNews):
    {totaal_nieuws}

    Jouw taak:
    Maak hier een razendsnelle, fascinerende 'Tech Update' van. 
    Kies de 3 allersterkste en meest interessante ontwikkelingen en vat die samen in exact 3 korte bulletpoints.

    Regels:
    - Elke bulletpoint mag maximaal 1 of 2 korte zinnen zijn.
    - Het moet direct weglezen: "Bedrijf X heeft Y uitgevonden, waardoor Z nu makkelijker gaat."
    - Geen langdradige inleidingen; kom direct ter zake. Leg boeiend maar kort uit wat de ontwikkeling is.
    - Schrijf in het Nederlands, zonder sensatie, en gebruik geen web-links.
    '''
    try:
                response = model.generate_content(prompt)
                return response.text
    except Exception as e:
         return f"Error: {e}"

def send_to_discord(ai_text):
        webhook_url = os.environ.get("TECH_NIEUWS_WEBHOOK")
    if not webhook_url: return
            content = f"** Tech Update **\n\n{ai_text}"
    requests.post(webhook_url, json={"content": content, "username": "Tech Overzicht"})

if __name__ == "__main__":
        top = get_top_stories()
    if top:
                txt = summarize_with_ai(top)
                if txt: send_to_discord(txt)
