import os
from openai import OpenAI
from .base_text_provider import BaseTextProvider

class OpenAITextProvider(BaseTextProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, conversation_history, system_prompt):
        messages = [{"role": "system", "content": system_prompt}] + conversation_history[-10:]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.4,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            print("🚨 OpenAI API Error:", e)
            return "Sorry, I couldn't generate an answer right now. Try again later."
