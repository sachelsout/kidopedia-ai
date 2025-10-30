import os
from dotenv import load_dotenv
from flask_cors import CORS
# Load environment variables from the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)
TEXT_PROVIDER=openai
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})