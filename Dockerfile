FROM python:3.12-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# Port FastAPI
EXPOSE 8000

# Lancement
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]