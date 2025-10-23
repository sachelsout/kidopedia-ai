import os
import requests
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

# ✅ Load environment variables
load_dotenv(dotenv_path="/Users/sha/Kidopedia-ai/kidopedia-ai/kideopedia/.env")
print("🧾 Loading from:", "/Users/sha/Kidopedia-ai/kidopedia-ai/kideopedia/.env")
print("🔑 Loaded key (preview):", os.getenv("OPENAI_API_KEY"))

# ✅ Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# ✅ Enable CORS for frontend connections
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.7.252:3001"
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# ✅ System prompt for consistent personality
SYSTEM_PROMPT = """
You are Kidopedia AI, a friendly and factually accurate educational assistant for children aged 7–12.

Your goals:
- Be fun, kind, and clear — but factually correct above all.
- Use child-friendly language while staying truthful and verifiable.
- If you are unsure about an answer, say: "I’m not sure, but I can find out!"
- Never make up facts, numbers, or names.

Reasoning Rules:
- Think step by step before responding.
- Prefer simple, real-world explanations over creative ones.
- When answering questions, focus on accuracy, brevity, and relevance.

Image Rules:
- If a user asks you to draw, show, illustrate, or create an image, DO NOT say you can’t draw.
- Instead, respond briefly and let the backend handle image creation.
- Your job is to confirm what will be drawn, for example: "Okay! I’ll draw a cat wearing a red hat for you! 🎨"
- Never include phrases like “I can’t show pictures” or “I can’t draw.”
- You can also describe or modify previous images safely when asked.
- Never describe unsafe, violent, or adult content.
"""

# ✅ Generate chat completion from OpenAI
def generate_ai_response(conversation_history):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[-10:]

    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.4,
        "top_p": 0.9,
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        if "choices" in response_json:
            assistant_reply = response_json["choices"][0]["message"]["content"]
        else:
            assistant_reply = "Sorry, I couldn't generate an answer right now. Try again later."
    except Exception as e:
        print("🚨 OpenAI Chat API Error:", e)
        assistant_reply = "Sorry, I couldn't generate an answer right now. Try again later."

    conversation_history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply, conversation_history


# ✅ Chat route
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    print("🧩 Incoming request data:", data)
    print("🧠 Session stored last image:", session.get("last_image_url"))

    user_message = data.get("message", "").strip()
    frontend_last_image = data.get("last_image_url")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    conversation_history = session.get("conversation_history", [])
    conversation_history.append({"role": "user", "content": user_message})

    assistant_reply, updated_history = generate_ai_response(conversation_history)
    image_url = None

    # ✅ Image generation
    is_image_prompt = any(keyword in user_message.lower() for keyword in ["draw", "show", "picture", "image", "illustrate"])
    if is_image_prompt:
        try:
            img_resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY').strip()}",
                    "Content-Type": "application/json"
                },
                json={"model": "dall-e-3", "prompt": user_message, "size": "1024x1024", "n": 1}
            )
            img_resp.raise_for_status()
            img_json = img_resp.json()
            image_url = img_json["data"][0]["url"]
            session["last_image_url"] = image_url
            print("💾 Saved last image to session:", image_url)
            assistant_reply = "Here’s your image! 🎨"
        except Exception as e:
            print("🚨 Image generation error:", e)
            assistant_reply = "I couldn't generate an image right now. Try again later."

    # ✅ Image edit (conceptual re-generation)
    edit_keywords = ["edit", "change", "alter", "modify", "replace", "add", "remove"]
    is_edit_request = any(word in user_message.lower() for word in edit_keywords)

    if is_edit_request:
        previous_image_url = data.get("last_image_url") or session.get("last_image_url")
        if previous_image_url:
            try:
                print("🎨 Conceptual edit based on previous image URL:", previous_image_url)
                new_prompt = (
                    f"Create a new version of the previous image ({previous_image_url}). "
                    f"The user wants to {user_message}. Keep the same subject, background, and artistic style."
                )

                edit_resp = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY').strip()}",
                        "Content-Type": "application/json"
                    },
                    json={"model": "dall-e-3", "prompt": new_prompt, "size": "1024x1024", "n": 1},
                    timeout=120
                )
                print("🖼️ Conceptual Edit API Status:", edit_resp.status_code)
                print("🧾 Conceptual Edit Raw Response:", edit_resp.text)
                edit_resp.raise_for_status()
                edit_json = edit_resp.json()
                image_url = edit_json["data"][0]["url"]
                session["last_image_url"] = image_url
                assistant_reply = "I’ve updated your image as you requested! 🎨"
            except Exception as e:
                print("🚨 Conceptual edit error:", e)
                assistant_reply = "I couldn’t update that picture right now. Try again later!"
        else:
            assistant_reply = "I don’t have a picture to edit yet! Try drawing one first. 🎨"

    session["conversation_history"] = updated_history

    return jsonify({"reply": assistant_reply, "image_url": image_url, "conversation": updated_history})


# ✅ Reset route
@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"message": "Conversation history reset successfully."})


if __name__ == "__main__":
    app.run(debug=True, port=8002)
