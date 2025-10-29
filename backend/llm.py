import os
import json
from pathlib import Path
from ai_providers.provider_factory import get_text_provider, get_image_provider
from dotenv import load_dotenv

# --- Load .env ---
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
root_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"🧾 Loaded .env from: {dotenv_path}")
elif os.path.exists(root_env_path):
    load_dotenv(root_env_path)
    print(f"🧾 Loaded .env from: {root_env_path}")
else:
    print("⚠️ No .env file found. Using system environment variables.")

# --- System prompt ---
SYSTEM_PROMPT = """
You are Kidopedia AI, a friendly and factually accurate educational assistant for children aged 7–12.
Be kind, use simple words, and keep your answers short (1-2 sentences).
You must remember the conversation history and answer follow-up questions based on previous messages.
"""

# --- Providers ---
text_provider = get_text_provider()
image_provider = get_image_provider()

# --- Memory directory for sessions ---
MEMORY_DIR = Path(__file__).parent / "user_memory"
MEMORY_DIR.mkdir(exist_ok=True)

def get_session_path(session_id: str) -> Path:
    return MEMORY_DIR / f"{session_id}.json"

def load_conversation(session_id: str):
    path = get_session_path(session_id)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_conversation(session_id: str, conversation):
    path = get_session_path(session_id)
    with open(path, "w") as f:
        json.dump(conversation, f, indent=2)

EDIT_KEYWORDS = ["edit", "change", "alter", "modify", "replace", "add", "remove", "put", "make", "give", "wear"]

def ask_question(user_message: str, session_id: str = "default_user", is_image_request: bool = False):
    conversation_history = load_conversation(session_id)
    conversation_history.append({"role": "user", "content": user_message})

    # --- Detect last image prompt ---
    last_image_prompt = None
    last_image_url = None
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant" and msg.get("image_prompt"):
            last_image_prompt = msg["image_prompt"]
        if msg.get("role") == "assistant" and msg.get("image_url"):
            last_image_url = msg["image_url"]
        if last_image_prompt and last_image_url:
            break

    image_url = None

    # --- Handle image edits ---
    if any(word in user_message.lower() for word in EDIT_KEYWORDS) and last_image_prompt:
        combined_prompt = f"{last_image_prompt}, but now {user_message.lower()}"
        print(f"🎨 Regenerating image with combined prompt: {combined_prompt}")
        image_url = image_provider.generate_image(combined_prompt)
        conversation_history.append({
            "role": "assistant",
            "content": "Here’s your updated image! 🎨",
            "image_url": image_url,
            "image_prompt": combined_prompt
        })

    # --- Handle new image request ---
    elif is_image_request:
        image_url = image_provider.generate_image(user_message)
        conversation_history.append({
            "role": "assistant",
            "content": "Here’s your image! 🎨",
            "image_url": image_url,
            "image_prompt": user_message
        })

    # --- Handle text generation ---
    else:
        reply = text_provider.generate_text(conversation_history, SYSTEM_PROMPT)
        conversation_history.append({"role": "assistant", "content": reply})

    save_conversation(session_id, conversation_history)
    last_reply = conversation_history[-1]["content"]
    return last_reply, image_url, conversation_history

# --- Flask integration ---
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default_user")
    is_image = any(word in user_message.lower() for word in ["draw", "show", "picture", "image"])
    
    reply, image_url, conversation = ask_question(
        user_message,
        session_id=session_id,
        is_image_request=is_image
    )

    return jsonify({
        "reply": reply,
        "image_url": image_url,
        "conversation": conversation,
        "session_id": session_id
    })

@app.route("/api/reset", methods=["POST"])
def reset_api():
    data = request.get_json() or {}
    session_id = data.get("session_id", "default_user")
    path = get_session_path(session_id)
    if path.exists():
        path.unlink()
    return jsonify({"message": f"Conversation history reset for {session_id}."})

if __name__ == "__main__":
    app.run(debug=True, port=8002)
