# Étape 1: Utiliser une image de base Python
FROM python:3.8-slim

# Étape 2: Installer les dépendances
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Étape 3: Copier le code source
COPY . /app/

# Étape 4: Exposer le port de l'application Flask
EXPOSE 5002

# Étape 5: Lancer l'application Flask
CMD ["python", "app.py"]
