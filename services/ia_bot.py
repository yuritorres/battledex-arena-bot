import os
from dotenv import load_dotenv
from google import genai

# Carregar variáveis do .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Novo client da SDK google.genai
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY não configurada."
    if not client:
        return "Cliente Gemini não inicializado."
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return f"Erro ao consultar Gemini: {e}"