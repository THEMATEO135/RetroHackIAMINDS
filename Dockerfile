# UPTC Energy AI - Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Exponer puertos
EXPOSE 8000 8501

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_URL=http://ollama:11434

# Comando por defecto (API)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
