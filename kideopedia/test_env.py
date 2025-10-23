from dotenv import load_dotenv
import os

env_path = "/Users/sha/Kidopedia-ai/kidopedia-ai/kideopedia/.env"
print(f"🧾 Loading from: {env_path}")

result = load_dotenv(dotenv_path=env_path)
print("📦 load_dotenv returned:", result)

key = os.getenv("OPENAI_API_KEY")
print("🔑 Loaded API key:", key)


