import os
from google import genai
from dotenv import load_dotenv

# 1. Load the .env file so we can access your secure keys
load_dotenv()

# 2. Grab the API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your .env file")

# 3. Initialize the Global Gemini Client (New SDK Standard)
client = genai.Client(api_key=api_key)

# 4. Set the default model (dynamically loaded from .env if available)
model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

print(f"[SYSTEM] Gemini AI successfully initialized using {model_name}")