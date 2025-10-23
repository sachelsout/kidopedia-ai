import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("🧾 Loaded .env from:", os.path.abspath(".env"))

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Enable CORS for frontend connections
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.7.252:3001"
    ]}},
    supports_credentials=True
)

# ---- Import providers ----
from ai_providers.provider_factory import get_text_provider, get_image_provider

text_provider = get_text_provider()
image_provider = get_image_provider()

# ---- System prompt for consistent personality ----
SYSTEM_PROMPT = """
You are Kidopedia AI, a friendly and factually accurate educational assistant for children aged 7–12.

Your goals:
- Be fun, kind, and clear — but factually correct above all.
- Answer in 1–2 short sentences using simple words suitable for kids.
- If you are unsure about an answer, say: "I’m not sure, but I can find out!"
- Never make up facts, numbers, or names.

Reasoning Rules:
- Think step by step before responding.
- Prefer simple, real-world explanations over creative ones.
- Remember previous conversation history and respond in context.
- When answering follow-up questions, relate them to prior messages.
- Focus on accuracy, brevity, and relevance.

Image Rules:
- If a user asks you to draw, show, illustrate, or create an image, respond briefly so the backend can handle image creation.
- Never include phrases like “I can’t show pictures” or “I can’t draw.”
- You can safely describe or modify previous images when asked.
- Never describe unsafe, violent, or adult content.
"""

# ---- Chat route ----
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    frontend_last_image = data.get("last_image_url")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    conversation_history = session.get("conversation_history", [])
    conversation_history.append({"role": "user", "content": user_message})

    # Generate AI response
    assistant_reply = text_provider.generate_text(conversation_history, system_prompt=SYSTEM_PROMPT)

    # Determine if image is needed
    image_keywords = ["draw", "show", "picture", "image", "illustrate"]
    edit_keywords = ["edit", "change", "alter", "modify", "replace", "add", "remove"]
    is_image_prompt = any(k in user_message.lower() for k in image_keywords)
    is_edit_request = any(k in user_message.lower() for k in edit_keywords)

    image_url = None
    if is_image_prompt or is_edit_request:
        try:
            prompt = user_message
            # If it's an edit, append previous image info
            if is_edit_request and frontend_last_image:
                prompt = f"Edit the previous image ({frontend_last_image}). {user_message}"

            image_url = image_provider.generate_image(prompt)
            session["last_image_url"] = image_url
            if image_url:
                assistant_reply = "Here’s your image! 🎨"
        except Exception as e:
            print("🚨 Image generation error:", e)
            assistant_reply = "I couldn’t generate an image right now. Try again later."

    # Save conversation
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    session["conversation_history"] = conversation_history

    return jsonify({
        "reply": assistant_reply,
        "image_url": image_url,
        "conversation": conversation_history
    })


# ---- Reset route ----
@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"message": "Conversation history reset successfully."})


if __name__ == "__main__":
    app.run(debug=True, port=8002)
