import os
import requests
from .base_image_provider import BaseImageProvider

class OpenAIImageProvider(BaseImageProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def generate_image(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": "1024x1024",
            "n": 1
        }

        try:
            response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
            response.raise_for_status()
            image_url = response.json()["data"][0]["url"]
        except Exception as e:
            print("🚨 OpenAI Image API Error:", e)
            image_url = None

        return image_url
