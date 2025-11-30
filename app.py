from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import de la fonction pour charger le modèle
from services.face_extractor import load_insightface_model

# Import du routeur
from api.endpoints import face

# --- GESTION DU LIFECYCLE (Remplace @app.on_event) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.
    - Avant yield : Startup (chargement du modèle)
    - Après yield : Shutdown (nettoyage)
    """
    # Startup
    print("🚀 Démarrage : Chargement du modèle InsightFace...")
    load_insightface_model()
    print("✅ Modèle chargé avec succès !")
    
    yield  # L'application tourne ici
    
    # Shutdown
    print("🛑 Arrêt : Nettoyage des ressources...")


# --- INITIALISATION DE L'APPLICATION ---

app = FastAPI(
    title="Vision Afrique Éthique API",
    description="Moteur de vision éthique - Structure modulaire",
    version="1.0.0",
    lifespan=lifespan  # ✅ Utilise le lifespan au lieu de on_event
)

# Inclusion des routes
app.include_router(face.router)

# Route de santé
@app.get("/", tags=["Santé"])
async def root():
    """Vérifie que l'API est en ligne."""
    return {"message": "API Vision Afrique Éthique en ligne."}

# Route de health check
@app.get("/health", tags=["Santé"])
async def health_check():
    """Vérifie l'état de l'API et de ses dépendances."""
    from services.face_extractor import INSIGHTFACE_MODEL
    
    return {
        "status": "healthy",
        "model_loaded": INSIGHTFACE_MODEL is not None,
        "version": "1.0.0"
    }