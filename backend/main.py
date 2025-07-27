import os
import joblib
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Spam and AI Detector API")

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    spam_model = joblib.load("spam_classifier.pkl")
except FileNotFoundError:
    raise RuntimeError("File not found! Make sure 'spam_classifier.pkl' is in the 'backend' directory.")

class TextIn(BaseModel):
    text: str

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

# ===============================================================
# NOTE: NEW DEBUGGING CHANGES ARE IN THIS FUNCTION
# ===============================================================
def get_ai_score_from_groq(text: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("DEBUG: GROQ_API_KEY not found in .env file.")
        return "API Key Missing"

    print(f"DEBUG: Calling Groq API with text: '{text[:50]}...'")

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI content detector. Analyze the user's text. Respond with ONLY a single number from 0 to 100 representing the percentage chance the text is AI-generated. Do not add any other words, symbols, or explanations. Just the number."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.1,
            },
            timeout=15 # Set a longer timeout to handle potentially slow responses
        )

        # Added for debugging to inspect the raw API response
        print(f"DEBUG: Groq API Status Code: {response.status_code}")
        print(f"DEBUG: Groq API Response: {response.text}")

        # Raise an HTTPError if the API response was not successful (e.g., 4xx or 5xx status codes)
        response.raise_for_status()

        data = response.json()
        ai_response_text = data['choices'][0]['message']['content']
        numbers = re.findall(r'\d+', ai_response_text)
        if numbers:
            return int(numbers[0])
        else:
            print(f"DEBUG: Groq did not return a number. Full response: {ai_response_text}")
            return "Could not parse AI score"

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Exception in Groq API: {e}")
        return "Error"
# ===============================================================

@app.post("/analyze")
def analyze_text(request: TextIn):
    cleaned_input_text = clean_text(request.text)
    prediction = spam_model.predict([cleaned_input_text])[0]
    spam_result = "Spam" if prediction == 1 else "Not Spam"

    ai_percentage = get_ai_score_from_groq(request.text)

    return {
        "spam_detection": {"result": spam_result, "prediction_code": int(prediction)},
        "ai_detection": {"percentage": ai_percentage}
    }

@app.get("/")
def root():
    return {"message": "API is running correctly"}
