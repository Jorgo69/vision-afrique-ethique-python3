# Import des classes FastAPI pour définir les routes
from fastapi import APIRouter, UploadFile, File, HTTPException

# Import de la fonction métier et du schéma de réponse
from services.face_extractor import extract_features_from_image, load_insightface_model
from core.models import FaceExtractionResponse
from core.config import settings # Sera utilisé pour la config/sécurité dans les phases futures


# Création du routeur. C'est l'équivalent de "routes/api.php" dans Laravel.
router = APIRouter(
    prefix="/face",         # Toutes les routes de ce fichier commenceront par /face
    tags=["Extraction"],    # Catégorie pour la documentation Swagger
)

# --- ROUTE : /extract ---

@router.post(
    "/extract", 
    response_model=FaceExtractionResponse, # Utilisation du schéma Pydantic pour la réponse
    status_code=200,
    summary="Extrait les features biométriques (embedding, âge, genre) d'un visage."
)
async def extract_features(
    image: UploadFile = File(..., description="Le fichier image (JPEG ou PNG) à analyser.")
):
    """
    Endpoint pour extraire les features d'un visage.
    Lit l'image, la passe au service, et renvoie l'âge, le genre, et l'embedding biométrique.
    """
    
    # 1. Lecture asynchrone des données de l'image
    image_bytes = await image.read()
    
    try:
        # 2. Appel du SERVICE (Séparation des préoccupations!)
        # Le Controller ne fait que de la plomberie HTTP et appelle la logique métier pure.
        features = extract_features_from_image(image_bytes)

    except RuntimeError as e:
        # Erreur si le modèle n'a pas été chargé (ex: dépendance manquante)
        # 500 Internal Server Error: Problème côté serveur
        raise HTTPException(
            status_code=500, detail=f"Erreur du service d'extraction: {e}"
        )
    except Exception:
        # Autres erreurs de traitement
        raise HTTPException(
            status_code=500, detail="Une erreur inattendue est survenue pendant l'extraction."
        )

    # 3. Gestion du résultat
    if features is None:
        # 400 Bad Request: L'image fournie n'a pas permis la détection
        raise HTTPException(
            status_code=400, detail="Aucun visage détecté ou image illisible."
        )

    # 4. Retourne les features. Pydantic s'assure que le format est respecté.
    return FaceExtractionResponse(
        age=features["age"],
        gender=features["gender"],
        embedding=features["embedding"]
    )