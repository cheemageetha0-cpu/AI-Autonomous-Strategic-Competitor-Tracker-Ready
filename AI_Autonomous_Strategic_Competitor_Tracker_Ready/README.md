# AI Autonomous Strategic Competitor Tracker

## Project structure
- .env - Gemini and/or Groq API key (never share or commit this file)
- .env.example - safe environment-variable template
- .gitignore - protects .env, venv and __pycache__
- test_gemini.py - tests the Gemini API connection
- app.py - Flask application
- agent.py - competitor analysis logic
- requirements.txt - Python dependencies
- static/style.css - styling
- static/script.js - dashboard and dynamic charts
- templates/index.html - input page
- templates/analysis.html - analysis dashboard

## Setup
1. Open PowerShell in this project folder.
2. Create/activate your virtual environment, or use the existing venv.
3. Install dependencies:
   .\\venv\\Scripts\\python.exe -m pip install -r requirements.txt
4. Copy `.env.example` to `.env`, then add `GEMINI_API_KEY`, `GROQ_API_KEY`, or both.
   The dashboard automatically uses Gemini, then Groq, then a local baseline if an API is unavailable.
   For quick demo responses, leave `WEB_RESEARCH_ENABLED=false`. Set it to `true` only when you want slower live web research.
5. Optional: test Gemini:
   .\\venv\\Scripts\\python.exe test_gemini.py
6. Start the app:
   .\\venv\\Scripts\\python.exe app.py
7. Open http://127.0.0.1:5000

The app discovers related competitors, compares strategic/capability scores using interactive bar and radar charts, explains each chart step-by-step, creates recommendations, and downloads a PDF report. API keys are only used by Flask on the server and never exposed in browser JavaScript.
