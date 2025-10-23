import os

# Text providers
from .text.openai_text_provider import OpenAITextProvider
from .text.openrouter_text_provider import OpenRouterTextProvider

# Image providers
from .image.openai_image_provider import OpenAIImageProvider
from .image.pollinations_image_provider import PollinationsImageProvider

# ---- Text Provider ----
def get_text_provider():
    provider_name = os.getenv("AI_TEXT_PROVIDER", "openai").lower()
    if provider_name == "openai":
        return OpenAITextProvider()
    elif provider_name == "openrouter":
        return OpenRouterTextProvider()
    else:
        raise ValueError(f"Unknown text provider: {provider_name}")

# ---- Image Provider ----
def get_image_provider():
    provider_name = os.getenv("AI_IMAGE_PROVIDER", "openai").lower()
    if provider_name == "openai":
        return OpenAIImageProvider()
    elif provider_name == "pollinations":
        return PollinationsImageProvider()
    else:
        raise ValueError(f"Unknown image provider: {provider_name}")
