import os
from .base_image_provider import BaseImageProvider

class PollinationsImageProvider(BaseImageProvider):
    def __init__(self):
        self.base_url = os.getenv("POLLINATIONS_BASE_URL", "https://image.pollinations.ai/prompt/")

    def generate_image(self, prompt):
        """
        Pollinations AI generates images directly via URL-based prompts.
        """
        # Convert spaces to %20 for URL encoding
        url_prompt = prompt.replace(" ", "%20")
        image_url = f"{self.base_url}{url_prompt}"
        return image_url
