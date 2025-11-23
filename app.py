# Import principal
from fastapi import FastAPI

# Import de la fonction pour charger le modèle de manière globale
from services.face_extractor import load_insightface_model

# Import du routeur (controller)
from api.endpoints import face

# --- INITIALISATION DE L'APPLICATION ---

app = FastAPI(
    title="Vision Afrique Éthique API",
    description="Moteur de vision éthique (Séparation des préoccupations - Structure modulaire)",
    version="1.0.0"
)

# 1. Configuration des événements de démarrage
@app.on_event("startup")
async def startup_event():
    """
    Exécuté au démarrage. Permet de charger les services coûteux une seule fois.
    """
    # Le chargement du modèle est délégué au service pour la logique métier
    load_insightface_model()


# 2. Inclusion des routes (Mapping de l'URL)
# Ceci rattache toutes les routes définies dans face.py à l'application principale.
# C'est ainsi que l'application reste légère et que les routes sont modulaires.
app.include_router(face.router)


# 3. Route de base (Santé/Health Check)
@app.get("/", tags=["Santé"])
async def root():
    """Vérifie que l'API est en ligne."""
    return {"message": "API Vision Afrique Éthique en ligne."}