# Dockerfile para o bot Telegram com integração Gemini
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências
RUN pip install --upgrade pip \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi \
    && pip install python-telegram-bot python-dotenv google-generativeai

# Copia o .env (opcional, pode ser montado via volume ou variável de ambiente)
# COPY .env /app/.env

# Comando padrão para rodar o bot principal (main.py)
CMD ["python", "main.py"]
