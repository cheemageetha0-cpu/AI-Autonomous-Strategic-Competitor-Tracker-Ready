import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key was not found.")
    print("Check that .env is in the same folder as test_gemini.py")
    exit()

print("API key found. Connecting to Gemini...")

client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1"}
)

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Explain competitor analysis in 3 simple sentences."
    )

    print("\n===== GEMINI TEST SUCCESSFUL =====\n")
    print(response.text)

except Exception as e:
    print("\n===== GEMINI TEST FAILED =====\n")
    print(type(e).__name__)
    print(e)