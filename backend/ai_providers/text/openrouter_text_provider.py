import os
import requests
from .base_text_provider import BaseTextProvider

class OpenRouterTextProvider(BaseTextProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    def generate_text(self, conversation_history, system_prompt):
        messages = [{"role": "system", "content": system_prompt}] + conversation_history[-10:]
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-20b:free",
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 150,
            "top_p": 0.9
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print("🚨 OpenRouter API Error:", e)
            return "Sorry, I couldn't generate an answer right now. Try again later."
