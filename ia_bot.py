import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis do .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY não configurada."
    try:
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"Erro ao consultar Gemini: {e}"