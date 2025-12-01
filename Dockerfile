# ============================================
# ÉTAPE 1 : Image de base
# ============================================
# On part de l'image officielle Python 3.11
# "slim" = version légère sans les outils inutiles (gagne de la place)
FROM python:3.11-slim

# ============================================
# ÉTAPE 2 : Configuration du conteneur
# ============================================
# Définit le dossier de travail (comme faire cd /app)
WORKDIR /app

# ============================================
# ÉTAPE 3 : Installer les dépendances système
# ============================================
# InsightFace + OpenCV ont besoin de nombreuses librairies système
# build-essential = compilateur g++ (nécessaire pour compiler InsightFace)
# python3-dev = headers Python (nécessaires pour compiler les extensions C)
# libsm6, libxext6, libxrender-dev = librairies OpenCV
# libgl1 = librairie OpenGL (critique pour cv2)
# libglib2.0-0 = dépendance de libgl1
# libgomp1 = pour le multi-threading
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# ÉTAPE 4 : Copier les requirements
# ============================================
# On copie juste requirements.txt d'abord
# (stratégie pour cache Docker : moins de rebuild)
COPY requirements.txt .

# ============================================
# ÉTAPE 5 : Installer les dépendances Python
# ============================================
# --no-cache-dir = économise de l'espace
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# ÉTAPE 6 : Copier tout le code
# ============================================
COPY . .

# ============================================
# ÉTAPE 7 : Exposer le port
# ============================================
# Expose le port 8000 (permet à Render de rediriger le trafic)
EXPOSE 8000

# ============================================
# ÉTAPE 8 : Commande de démarrage
# ============================================
# Lance uvicorn sur 0.0.0.0:8000
# 0.0.0.0 = écoute sur TOUTES les interfaces réseau (important pour Render)
# --host 0.0.0.0 = accessible depuis l'extérieur
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]