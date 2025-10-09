from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend (Vercel) to make requests

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Kidopedia AI backend!"})

@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Placeholder AI logic
    response = f"This is a placeholder answer for: {question}"

    return jsonify({
        "question": question,
        "answer": response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)