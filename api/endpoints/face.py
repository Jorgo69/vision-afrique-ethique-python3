# Import des classes FastAPI pour définir les routes
from fastapi import APIRouter, UploadFile, File, HTTPException, Form # <-- Import de Form

# Import de la fonction métier et du schéma de réponse
from services.face_extractor import extract_features_from_image, load_insightface_model
from core.models import FaceExtractionResponse, TokenizeResponse
from core.config import settings # Sera utilisé pour la config/sécurité dans les phases futures
from security import hash_embedding # <-- Importation du service de sécurité
from security import verify_token # <-- Import de la fonction de vérification
from core.models import MatchResponse


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
    
# --- NOUVELLE ROUTE : /tokenize ---

@router.post(
    "/tokenize", 
    response_model=TokenizeResponse, 
    status_code=200,
    summary="Extrait les features et génère un token cryptographique irréversible."
)
async def tokenize_face(
    image: UploadFile = File(..., description="Le fichier image du visage à sécuriser.")
):
    """
    Endpoint de la Phase 2. 
    1. Extrait l'embedding brut.
    2. Hache l'embedding en utilisant le double hashage salé (Argon2) avec les secrets.
    3. Ne retourne que le token et les métadonnées (Age, Genre).
    """
    
    # 1. Lecture asynchrone des données de l'image
    image_bytes = await image.read()
    
    try:
        # 2. Appel du SERVICE d'extraction
        features = extract_features_from_image(image_bytes)

    except RuntimeError as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur du service d'extraction: {e}"
        )
    except Exception:
        raise HTTPException(
            status_code=500, detail="Une erreur inattendue est survenue pendant l'extraction."
        )

    # 3. Gestion de l'échec de détection
    if features is None:
        raise HTTPException(
            status_code=400, detail="Aucun visage détecté ou image illisible."
        )

    # 4. Phase Critique : Hachage de l'Embedding
    # L'embedding brut est ici traité, mais NE DOIT JAMAIS être stocké ou loggué !
    embedding_brut = features["embedding"]
    
    try:
        # Appel du SERVICE DE SÉCURITÉ (Hashage irréversible)
        security_token = hash_embedding(embedding_brut)
        
    except RuntimeError as e:
        # Erreur si le hachage échoue (ex: secret manquant)
        raise HTTPException(
            status_code=500, detail=f"Échec de la création du token sécurisé: {e}"
        )

    # 5. Retourne le token et les métadonnées (SANS l'embedding brut)
    return TokenizeResponse(
        age=features["age"],
        gender=features["gender"],
        token=security_token
    )
    
# --- Fin du fichier : l'endpoint /extract existe toujours en dessous ---

# --- NOUVELLE ROUTE : /match ---

@router.post(
    "/match", 
    response_model=MatchResponse, 
    status_code=200,
    summary="Vérifie si le visage dans l'image correspond au token de référence fourni."
)
async def match_face_token(
    # Fichier image soumis par le client
    image: UploadFile = File(..., description="Le fichier image du visage à vérifier."),
    # Token de référence (doit être envoyé comme champ de formulaire "token_reference")
    token_reference: str = Form(..., description="Le token Argon2 ($argon2id$...) de référence.")
):
    """
    Endpoint de vérification.
    1. Extrait l'embedding brut de l'image.
    2. Utilise cet embedding brut et le token de référence pour vérifier la correspondance.
    3. Ne renvoie JAMAIS les embeddings ou les tokens bruts.
    """
    
    # 1. Lecture des données
    image_bytes = await image.read()
    
    try:
        # 2. Extraction du nouvel embedding (Étape 1 du process)
        features = extract_features_from_image(image_bytes)

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Erreur du service d'extraction: {e}")

    # 3. Vérification de l'échec de détection
    if features is None:
        raise HTTPException(
            status_code=400, detail="Aucun visage détecté sur l'image à vérifier."
        )

    # 4. Phase Critique : Vérification du Token
    # Le nouvel embedding est utilisé pour la vérification, sans être chiffré une deuxième fois
    # (Argon2 est déterministe par rapport au couple (input+salt) fourni)
    
    embedding_brut_actuel = features["embedding"]
    
    try:
        # Appel du SERVICE DE SÉCURITÉ : utilise le nouvel embedding pour recréer l'input 
        # SHA-256/Secret et le comparer au token_reference stocké.
        is_match = verify_token(embedding_brut_actuel, token_reference)
        
    except Exception as e:
        # Erreur lors de la vérification (souvent due à un token_reference mal formé)
        raise HTTPException(
            status_code=422, detail=f"Erreur de validation du token de référence : {e}"
        )

    # 5. Retour de la réponse
    if is_match:
        return MatchResponse(
            match_found=True,
            detail="Correspondance d'identité vérifiée."
        )
    else:
        return MatchResponse(
            match_found=False,
            detail="Le visage ne correspond pas au token de référence."
        )