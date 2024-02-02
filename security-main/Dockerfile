# Utilisez une image Python officielle en tant qu'image de base
FROM python:3.8

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Mise à jour de pip
RUN pip install --upgrade pip

# Installez les dépendances Python
RUN pip install -r requirements.txt

# Copiez tout le contenu actuel dans le conteneur
COPY . .

# Commande à exécuter lors du démarrage du conteneur
CMD ["python", "app.py"]
