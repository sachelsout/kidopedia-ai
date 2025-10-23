import os
import requests
from .base_text_provider import BaseTextProvider

class OpenAITextProvider(BaseTextProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def generate_text(self, conversation_history, system_prompt):
        messages = [{"role": "system", "content": system_prompt}] + conversation_history[-10:]
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.4,
            "top_p": 0.9
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            assistant_reply = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print("🚨 OpenAI API Error:", e)
            assistant_reply = "Sorry, I couldn't generate an answer right now. Try again later."

        return assistant_reply
