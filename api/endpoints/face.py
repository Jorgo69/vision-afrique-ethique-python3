"""
Endpoints de l'API de reconnaissance faciale.
Gestion d'erreurs améliorée avec codes standardisés.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.face_extractor import extract_features_from_image
from core.models import FaceExtractionResponse, TokenizeResponse, MatchResponse
from core.errors import ErrorCode, get_error_response
from security import hash_embedding, verify_token

# Limites de sécurité
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]

# Création du routeur
router = APIRouter(
    prefix="/face",
    tags=["Extraction"],
)


# ============================================
# FONCTION UTILITAIRE : Validation d'Image
# ============================================

async def validate_image(image: UploadFile) -> bytes:
    """
    Valide une image uploadée.
    
    Returns:
        bytes: Les bytes de l'image si valide
    
    Raises:
        HTTPException: Si l'image est invalide
    """
    # Validation 1 : Type de contenu
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.INVALID_IMAGE_FORMAT)
        )
    
    # Validation 2 : Taille
    image_bytes = await image.read()
    
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.IMAGE_CORRUPTED)
        )
    
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.IMAGE_TOO_LARGE)
        )
    
    return image_bytes


# ============================================
# ROUTE 1 : /extract
# ============================================

@router.post(
    "/extract",
    response_model=FaceExtractionResponse,
    status_code=200,
    summary="Extrait les features biométriques d'un visage"
)
async def extract_features(
    image: UploadFile = File(..., description="Image JPEG, PNG ou WebP (max 10MB)")
):
    """
    Extrait l'âge, le genre et l'embedding biométrique d'un visage.
    
    **Codes d'erreur possibles :**
    - `NO_FACE_DETECTED` : Aucun visage dans l'image
    - `IMAGE_TOO_LARGE` : Image > 10MB
    - `IMAGE_CORRUPTED` : Image illisible
    - `INVALID_IMAGE_FORMAT` : Format non supporté
    - `IMAGE_TOO_SMALL` : Dimensions < 200x200
    - `MODEL_NOT_LOADED` : Modèle non initialisé
    """
    
    # Validation de l'image
    image_bytes = await validate_image(image)
    
    try:
        # Appel du service d'extraction
        features = extract_features_from_image(image_bytes)
    
    except RuntimeError as e:
        # Erreur de modèle non chargé
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.MODEL_NOT_LOADED)
        )
    
    except ValueError as e:
        # Erreurs de validation d'image
        error_msg = str(e)
        
        if "IMAGE_CORRUPTED" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=get_error_response(ErrorCode.IMAGE_CORRUPTED)
            )
        elif "IMAGE_TOO_SMALL" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=get_error_response(ErrorCode.IMAGE_TOO_SMALL)
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=get_error_response(ErrorCode.EXTRACTION_FAILED)
            )
    
    except Exception as e:
        # Erreur inattendue
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.EXTRACTION_FAILED)
        )
    
    # Gestion du cas "aucun visage détecté"
    if features is None:
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.NO_FACE_DETECTED)
        )
    
    # Retourne les features
    return FaceExtractionResponse(
        age=features["age"],
        gender=features["gender"],
        embedding=features["embedding"]
    )


# ============================================
# ROUTE 2 : /tokenize
# ============================================

@router.post(
    "/tokenize",
    response_model=TokenizeResponse,
    status_code=200,
    summary="Génère un token cryptographique sécurisé"
)
async def tokenize_face(
    image: UploadFile = File(..., description="Image JPEG, PNG ou WebP (max 10MB)")
):
    """
    Extrait les features et génère un token Argon2 irréversible.
    
    **Le token peut être stocké en base de données de manière sécurisée.**
    L'embedding biométrique brut n'est JAMAIS retourné.
    
    **Codes d'erreur possibles :**
    - Mêmes codes que `/extract`
    - `HASHING_FAILED` : Échec de la génération du token
    """
    
    # Validation de l'image
    image_bytes = await validate_image(image)
    
    try:
        # Extraction des features
        features = extract_features_from_image(image_bytes)
    
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.MODEL_NOT_LOADED)
        )
    
    except ValueError as e:
        error_msg = str(e)
        
        if "IMAGE_CORRUPTED" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=get_error_response(ErrorCode.IMAGE_CORRUPTED)
            )
        elif "IMAGE_TOO_SMALL" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=get_error_response(ErrorCode.IMAGE_TOO_SMALL)
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=get_error_response(ErrorCode.EXTRACTION_FAILED)
            )
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.EXTRACTION_FAILED)
        )
    
    # Aucun visage détecté
    if features is None:
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.NO_FACE_DETECTED)
        )
    
    # Hachage de l'embedding
    embedding_brut = features["embedding"]
    
    try:
        security_token = hash_embedding(embedding_brut)
    
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.HASHING_FAILED)
        )
    
    # Retourne le token et les métadonnées (SANS l'embedding)
    return TokenizeResponse(
        age=features["age"],
        gender=features["gender"],
        token=security_token
    )


# ============================================
# ROUTE 3 : /match
# ============================================

@router.post(
    "/match",
    response_model=MatchResponse,
    status_code=200,
    summary="Vérifie la correspondance visage-token"
)
async def match_face_token(
    image: UploadFile = File(..., description="Image à vérifier"),
    token_reference: str = Form(..., description="Token Argon2 de référence")
):
    """
    Vérifie si le visage dans l'image correspond au token de référence.
    
    **Cas d'usage :**
    - Authentification biométrique
    - Vérification d'identité
    - Contrôle d'accès
    
    **Codes d'erreur possibles :**
    - Mêmes codes que `/tokenize`
    - `INVALID_TOKEN_FORMAT` : Token mal formé
    - `TOKEN_VERIFICATION_FAILED` : Token valide mais pas de correspondance
    """
    
    # Validation du token
    if not token_reference.startswith("$argon2id$"):
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.INVALID_TOKEN_FORMAT)
        )
    
    # Validation de l'image
    image_bytes = await validate_image(image)
    
    try:
        # Extraction des features
        features = extract_features_from_image(image_bytes)
    
    except RuntimeError:
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.MODEL_NOT_LOADED)
        )
    
    except ValueError as e:
        error_msg = str(e)
        
        if "IMAGE_CORRUPTED" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=get_error_response(ErrorCode.IMAGE_CORRUPTED)
            )
        elif "IMAGE_TOO_SMALL" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=get_error_response(ErrorCode.IMAGE_TOO_SMALL)
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=get_error_response(ErrorCode.EXTRACTION_FAILED)
            )
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=get_error_response(ErrorCode.EXTRACTION_FAILED)
        )
    
    # Aucun visage détecté
    if features is None:
        raise HTTPException(
            status_code=400,
            detail=get_error_response(ErrorCode.NO_FACE_DETECTED)
        )
    
    # Vérification du token
    embedding_brut_actuel = features["embedding"]
    
    try:
        is_match = verify_token(embedding_brut_actuel, token_reference)
    
    except Exception:
        raise HTTPException(
            status_code=422,
            detail=get_error_response(ErrorCode.INVALID_TOKEN_FORMAT)
        )
    
    # Retourne le résultat
    if is_match:
        return MatchResponse(
            match_found=True,
            detail="Correspondance d'identité vérifiée avec succès."
        )
    else:
        return MatchResponse(
            match_found=False,
            detail="Le visage ne correspond pas au token de référence."
        )