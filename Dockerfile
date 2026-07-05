# On utilise une version stable et légère de Python
FROM python:3.9-slim

WORKDIR /app

# Mises à jour minimales (On a retiré software-properties-common qui plantait)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requis
COPY requirements.txt .

# Installation des dépendances Python (avec une option pour éviter les erreurs de cache)
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie du reste du code
COPY . .

# Configuration du port
EXPOSE 8501

# Commande de lancement
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]