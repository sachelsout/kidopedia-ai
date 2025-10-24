import flask
if not hasattr(flask.Flask, "session_cookie_name"):
    flask.Flask.session_cookie_name = "session"  # Compatibility fix for Flask 3.x

import os
import json
import uuid
import requests
from flask import Flask, request, jsonify, session
from flask_session import Session
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

# ✅ Configure server-side session storage
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_FILE_DIR"] = "./flask_session_data"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
Session(app)

# ✅ Enable CORS for local dev
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# ✅ Create user memory folder if missing
MEMORY_DIR = "./user_memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

def get_session_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]

def load_user_memory(session_id):
    path = os.path.join(MEMORY_DIR, f"{session_id}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_user_memory(session_id, data):
    path = os.path.join(MEMORY_DIR, f"{session_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

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
- Smaller sentences, that a child can comprehend.  

Image Rules:
- If a user asks you to draw, show, illustrate, or create an image, DO NOT say you can’t draw.
- Instead, respond briefly and let the backend handle image creation.
- Your job is to confirm what will be drawn, for example: "Okay! I’ll draw a cat wearing a red hat for you! 🎨"
- Never include phrases like “I can’t show pictures” or “I can’t draw.”
- You can also describe or modify previous images safely when asked.
- Never describe unsafe, violent, or adult content.
"""

# ✅ Generate chat completion

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
        assistant_reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't generate an answer right now.")
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

    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    session_id = get_session_id()
    conversation_history = load_user_memory(session_id)

    conversation_history.append({"role": "user", "content": user_message})
    assistant_reply, updated_history = generate_ai_response(conversation_history)

    image_url = None
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
            image_url = img_resp.json()["data"][0]["url"]
            updated_history.append({"role": "assistant", "content": "Here’s your image! 🎨"})
        except Exception as e:
            print("🚨 Image generation error:", e)

    edit_keywords = ["edit", "change", "alter", "modify", "replace", "add", "remove", "put", "make", "give", "wear"]
    if any(word in user_message.lower() for word in edit_keywords):
        try:
            new_prompt = f"Modify the last image to: {user_message}. Keep it kid-friendly and fun."
            edit_resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY').strip()}",
                    "Content-Type": "application/json"
                },
                json={"model": "dall-e-3", "prompt": new_prompt, "size": "1024x1024", "n": 1},
                timeout=120
            )
            edit_resp.raise_for_status()
            image_url = edit_resp.json()["data"][0]["url"]
            updated_history.append({"role": "assistant", "content": "I’ve updated your image as you requested! 🎨"})
        except Exception as e:
            print("🚨 Conceptual edit error:", e)

    save_user_memory(session_id, updated_history)
    print(f"🧠 Memory saved for session {session_id}")

    return jsonify({"reply": updated_history[-1]["content"], "image_url": image_url, "conversation": updated_history})

# ✅ Reset route
@app.route("/api/reset", methods=["POST"])
def reset():
    session_id = get_session_id()
    path = os.path.join(MEMORY_DIR, f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
    session.clear()
    print(f"🧹 Session cleared for {session_id}")
    return jsonify({"message": "Conversation history reset successfully."})

if __name__ == "__main__":
    app.run(debug=True, port=8002)