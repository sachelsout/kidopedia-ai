import flask
if not hasattr(flask.Flask, "session_cookie_name"):
    flask.Flask.session_cookie_name = "session"

import os
import sys
import json
import requests
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# --- Environment Setup ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

if not ENV_PATH.exists():
    print(f"⚠️  .env not found at {ENV_PATH}")
else:
    print(f"🧾 Loading .env from: {ENV_PATH}")
    load_dotenv(dotenv_path=ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file.")
else:
    OPENAI_API_KEY = OPENAI_API_KEY.strip()
    print("🔑 Loaded OpenAI key (first 10 chars):", OPENAI_API_KEY[:10])

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
}}, supports_credentials=True)

MEMORY_DIR = Path(__file__).resolve().parent / "user_memory"
MEMORY_DIR.mkdir(exist_ok=True)

def get_session_path(session_id: str) -> Path:
    return MEMORY_DIR / f"{session_id}.json"

def load_conversation(session_id: str):
    path = get_session_path(session_id)
    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
            return data
    return []

def save_conversation(session_id: str, conversation):
    path = get_session_path(session_id)
    with open(path, "w") as f:
        json.dump(conversation, f, indent=2)

SYSTEM_PROMPT = """
You are Kidopedia AI, a friendly, factually correct educational assistant for kids aged 7–12.
Keep answers fun, simple, and true. If you don’t know something, say “I’m not sure, but I can find out!”.
When summarizing, use short, cheerful sentences like: “Earlier we talked about how the Wright brothers built airplanes!”
"""

def summarize_conversation(history):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    summary_prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Summarize this conversation in a short, friendly way for kids:"},
        {"role": "assistant", "content": str(history)}
    ]
    data = {"model": "gpt-4o-mini", "messages": summary_prompt, "temperature": 0.5}
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "We talked about fun facts!")
        return {"role": "system", "content": summary}
    except Exception as e:
        print("🚨 Summarization error:", e)
        return {"role": "system", "content": "Earlier we talked about some cool topics!"}

def generate_ai_response(conversation_history):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    if len(conversation_history) > 20:
        print("🧠 Conversation too long — summarizing older context...")
        summary_message = summarize_conversation(conversation_history[:-10])
        conversation_history = [summary_message] + conversation_history[-10:]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[-10:]
    data = {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.4, "top_p": 0.9}

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        assistant_reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't generate an answer right now.")
    except Exception as e:
        print("🚨 OpenAI Chat API Error:", e)
        assistant_reply = "Sorry, I couldn't generate an answer right now. Try again later."

    conversation_history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply, conversation_history

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id") or "default_user"

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    conversation_history = load_conversation(session_id)
    conversation_history.append({"role": "user", "content": user_message})

    # Detect edit intent before generating AI response
    edit_keywords = ["edit", "change", "alter", "modify", "replace", "add", "remove", "put", "make", "give", "wear"]
    last_image_url = None
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant" and msg.get("image_url"):
            last_image_url = msg["image_url"]
            break

    # Skip direct binary image edits and handle via DALL·E 3 regeneration instead
    if any(word in user_message.lower() for word in edit_keywords) and last_image_url:
        print("🖼️ Detected edit intent — skipping DALL·E 2 direct upload. Using DALL·E 3 contextual regeneration instead.")
        pass  # Let the DALL·E 3 regeneration logic below handle it

    assistant_reply, updated_history = generate_ai_response(conversation_history)

    image_url = None
    is_image_prompt = any(k in user_message.lower() for k in ["draw", "show", "picture", "image", "illustrate"])
    edit_keywords = ["edit", "change", "alter", "modify", "replace", "add", "remove", "put", "make", "give", "wear"]

    last_image_url = None
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant" and msg.get("image_url"):
            last_image_url = msg["image_url"]
            break

    if is_image_prompt:
        try:
            img_resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": "dall-e-3", "prompt": user_message, "size": "1024x1024", "n": 1}
            )
            img_resp.raise_for_status()
            image_url = img_resp.json()["data"][0]["url"]
            updated_history.append({
                "role": "assistant",
                "content": "Here’s your image! 🎨",
                "image_url": image_url,
                "image_prompt": user_message
            })
        except Exception as e:
            print("🚨 Image generation error:", e)

    elif any(word in user_message.lower() for word in edit_keywords) and last_image_url:
        try:
            previous_prompt = None
            for msg in reversed(conversation_history):
                if msg.get("role") == "assistant" and msg.get("image_prompt"):
                    previous_prompt = msg["image_prompt"]
                    break

            base_prompt = previous_prompt or "a fun kid-friendly illustration"
            combined_prompt = f"{base_prompt}, but now {user_message.lower()}"

            print(f"🎨 Using combined prompt for edit: {combined_prompt}")

            # Regenerate image using DALL·E 3
            img_regen_resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": "dall-e-3", "prompt": combined_prompt, "size": "1024x1024", "n": 1}
            )
            img_regen_resp.raise_for_status()

            image_url = img_regen_resp.json()["data"][0]["url"]

            updated_history.append({
                "role": "assistant",
                "content": "Here’s your updated image! 🎨 (Generated using DALL·E 3)",
                "image_url": image_url,
                "image_prompt": combined_prompt
            })

            save_conversation(session_id, updated_history)
            return jsonify({
                "reply": "Here’s your updated image! 🎨 (Generated using DALL·E 3)",
                "image_url": image_url,
                "conversation": updated_history,
                "session_id": session_id
            })

        except Exception as e:
            print("🚨 Image edit error:", e)
            return jsonify({
                "reply": "Sorry, I couldn't edit the image right now. Please try again.",
                "conversation": conversation_history,
                "session_id": session_id
            })

    save_conversation(session_id, updated_history)

    return jsonify({"reply": updated_history[-1]["content"], "image_url": image_url, "conversation": updated_history, "session_id": session_id})

@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json() or {}
    session_id = data.get("session_id") or "default_user"
    path = get_session_path(session_id)
    if path.exists():
        path.unlink()
    return jsonify({"message": f"Conversation history reset for {session_id}."})

if __name__ == "__main__":
    app.run(debug=True, port=8002)