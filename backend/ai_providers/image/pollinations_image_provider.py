import os
import requests
from .base_image_provider import BaseImageProvider

class PollinationsImageProvider(BaseImageProvider):
    def __init__(self):
        self.base_url = os.getenv("POLLINATIONS_BASE_URL", "https://image.pollinations.ai/prompt/")

    def generate_image(self, prompt: str) -> str:
        try:
            # Pollinations API uses simple GET request
            url = f"{self.base_url}{requests.utils.quote(prompt)}"
            return url
        except Exception as e:
            print("🚨 Pollinations error:", e)
            return "Error generating image"
