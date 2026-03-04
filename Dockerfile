# syntax=docker/dockerfile:1.6

# Dockerfile para o bot Telegram com integração Gemini
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia apenas o arquivo de dependências para aproveitar o cache de camadas
COPY requirements.txt ./

# Instala dependências utilizando cache de download do pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia os arquivos do projeto
COPY . /app

# Copia o .env (opcional, pode ser montado via volume ou variável de ambiente)
# COPY .env /app/.env

# Comando padrão para rodar o bot principal (main.py)
CMD ["python", "main.py"]
