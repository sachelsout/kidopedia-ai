import os
from dotenv import load_dotenv
load_dotenv()
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import generate_ai_response

app = Flask(__name__)
CORS(app)  # allow frontend (Vercel) to make requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # reuse your current env var
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Kidopedia AI backend!"})

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"error": "No question provided"}), 400

    try:
        answer = generate_ai_response(user_input)
    except Exception as e:
        print("AI API error:", e)
        # Fallback response if AI fails
        answer = "Oops! I couldn't generate an answer right now. Try asking something else."

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gryphe/mythomax-l2-13b",
            "messages": [
                {"role": "system", "content": "You are a creative assistant that generates kid-friendly image prompts and descriptions."},
                {"role": "user", "content": f"Describe a cute, kid-friendly, soft pastel cartoon illustration showing {user_input}. Use bright colors, playful style, and simple shapes suitable for children aged 8. Also provide a short, fun image description for kids."}
            ]
        }
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        image_prompt = result["choices"][0]["message"]["content"]

        import urllib.parse
        print("Raw image prompt:", image_prompt)
        encoded_prompt = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote_plus(image_prompt)}"
        print("Generated image URL:", image_url)

        # Extract image description from the prompt if possible
        # Assuming the description is separated by a delimiter or in a certain format,
        # but since we only get one content, let's just return the prompt as description too.
        image_description = image_prompt

    except Exception as e:
        print("OpenRouter image generation error:", e)
        image_url = ""
        image_description = ""

    return jsonify({
        "question": user_input,
        "answer": answer,
        "image_url": image_url,
        "image_description": image_description
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)