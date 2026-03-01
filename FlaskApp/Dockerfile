# Dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# instalar dependencias del sistema necesarias para Chromium / Chromedriver
RUN apt-get update && apt-get install -y \
    wget gnupg unzip ca-certificates fonts-liberation \
    libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libx11-6 libx11-xcb1 libxcb1 libxrandr2 libasound2 libgbm1 \
    chromium chromium-driver --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la app
COPY . .

# Por si quieres un path por defecto al chromedriver en el contenedor
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Exponer puerto (usado por docker run y Cloud Run)
EXPOSE ${PORT}

# Comando para arrancar: asume main.py contiene "app = Flask(__name__)"
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "120", "app:app"]
