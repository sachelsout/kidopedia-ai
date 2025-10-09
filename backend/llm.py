import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are Kidopedia AI, a friendly and fun educational assistant for children.
Answer the question in a way that a child (ages 7 to 12) can easily understand, using simple words.
Keep your answer short: 1 to 2 lines maximum.
Make it engaging, fun, and clear. Do not use technical terms that a kid might not understand.
"""

def generate_ai_response(prompt, retries=10, delay=2):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"Rate limit hit, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("HTTP error:", e)
                break
        except Exception as e:
            print("Error during AI request:", e)
            break

    return "Sorry, I couldn't generate an answer right now. Try again later."
