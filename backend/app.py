from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import generate_ai_response

app = Flask(__name__)
CORS(app)  # allow frontend (Vercel) to make requests

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

    return jsonify({
        "question": user_input,
        "answer": answer
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)