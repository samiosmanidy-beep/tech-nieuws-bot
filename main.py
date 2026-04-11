import os
import requests

def get_top_stories():
    """Haalt de top 5 verhalen op van Hacker News"""
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url)
        response.raise_for_status()
        story_ids = response.json()[:5]

        stories = []
        for story_id in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_res = requests.get(story_url)
            if story_res.status_code == 200:
                story_data = story_res.json()
                if story_data and "url" in story_data and "title" in story_data:
                    stories.append(f"{story_data['title']}\n{story_data['url']}")
        
        return stories
    except Exception as e:
        print(f"Fout bij het ophalen van nieuws: {e}")
        return []

def send_to_discord(stories):
    """Verstuurt het nieuws direct via een Discord webhook"""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Fout: DISCORD_WEBHOOK_URL is niet ingesteld.")
        return

    content = "\n\n".join(stories)
    if len(content) > 1900:
        content = content[:1896] + "..."
        
    data = {
        "content": content,
        "username": "Tech Info"
    }

    try:
        res = requests.post(webhook_url, json=data)
        if res.status_code in [200, 204]:
            print("Succesvol verstuurd naar Discord!")
        else:
            print(f"Kon niet versturen. Status code: {res.status_code}, Response: {res.text}")
    except Exception as e:
        print(f"Fout bij het versturen naar Discord: {e}")

if __name__ == "__main__":
    top_stories = get_top_stories()
    if top_stories:
        send_to_discord(top_stories)
    else:
        print("Geen nieuws gevonden om te versturen.")
