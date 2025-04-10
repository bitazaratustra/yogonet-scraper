FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1 \
    BQ_TABLE_ID=yogonet-456319.yogonet_data.articles \
    TIMEOUT_SECONDS=300

# Configurar repositorios esenciales
RUN echo "deb http://deb.debian.org/debian buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list

# Instalar dependencias críticas
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Ejecutar main.py directamente en lugar de servir la API
CMD ["python", "main.py"]
