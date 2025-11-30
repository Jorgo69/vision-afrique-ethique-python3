"""
Codes d'erreur standardisés pour l'API.
Chaque erreur a un code unique et un message clair.
"""

from enum import Enum
from typing import Dict, Any

class ErrorCode(str, Enum):
    """Codes d'erreur de l'API."""
    
    # Erreurs d'image (400)
    NO_FACE_DETECTED = "NO_FACE_DETECTED"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    IMAGE_CORRUPTED = "IMAGE_CORRUPTED"
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"
    IMAGE_TOO_SMALL = "IMAGE_TOO_SMALL"
    
    # Erreurs de token (400)
    INVALID_TOKEN_FORMAT = "INVALID_TOKEN_FORMAT"
    TOKEN_VERIFICATION_FAILED = "TOKEN_VERIFICATION_FAILED"
    
    # Erreurs serveur (500)
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    HASHING_FAILED = "HASHING_FAILED"
    
    # Erreurs de validation (422)
    MISSING_IMAGE = "MISSING_IMAGE"
    MISSING_TOKEN = "MISSING_TOKEN"


class APIError:
    """Constructeur d'erreurs standardisées."""
    
    @staticmethod
    def format_error(code: ErrorCode, message: str, details: str = None) -> Dict[str, Any]:
        """
        Formate une erreur en JSON standard.
        
        Args:
            code: Code d'erreur (enum)
            message: Message principal
            details: Détails supplémentaires (optionnel)
        
        Returns:
            Dict formaté pour FastAPI HTTPException
        """
        error = {
            "error": {
                "code": code.value,
                "message": message
            }
        }
        
        if details:
            error["error"]["details"] = details
        
        return error


# ============================================
# Messages d'Erreur Prédéfinis
# ============================================

ERROR_MESSAGES = {
    ErrorCode.NO_FACE_DETECTED: {
        "message": "Aucun visage détecté dans l'image",
        "details": "Assurez-vous que :\n- Le visage est visible et bien cadré\n- L'image est bien éclairée\n- Le visage occupe au moins 20% de l'image"
    },
    
    ErrorCode.IMAGE_TOO_LARGE: {
        "message": "Image trop volumineuse",
        "details": "Taille maximale autorisée : 10 MB. Compressez l'image ou réduisez sa résolution."
    },
    
    ErrorCode.IMAGE_CORRUPTED: {
        "message": "Image corrompue ou illisible",
        "details": "Le fichier ne peut pas être décodé. Vérifiez que c'est une image valide (JPEG, PNG, WebP)."
    },
    
    ErrorCode.INVALID_IMAGE_FORMAT: {
        "message": "Format d'image non supporté",
        "details": "Formats acceptés : JPEG (.jpg, .jpeg), PNG (.png), WebP (.webp)"
    },
    
    ErrorCode.IMAGE_TOO_SMALL: {
        "message": "Image trop petite",
        "details": "Dimensions minimales : 200x200 pixels. Utilisez une image de meilleure qualité."
    },
    
    ErrorCode.INVALID_TOKEN_FORMAT: {
        "message": "Format de token invalide",
        "details": "Le token doit être au format Argon2 ($argon2id$...)"
    },
    
    ErrorCode.TOKEN_VERIFICATION_FAILED: {
        "message": "Échec de la vérification du token",
        "details": "Le token est valide mais ne correspond pas au visage fourni."
    },
    
    ErrorCode.MODEL_NOT_LOADED: {
        "message": "Modèle de reconnaissance faciale non chargé",
        "details": "Erreur serveur : le service est en cours d'initialisation. Réessayez dans quelques secondes."
    },
    
    ErrorCode.EXTRACTION_FAILED: {
        "message": "Échec de l'extraction des features",
        "details": "Une erreur inattendue est survenue pendant le traitement de l'image."
    },
    
    ErrorCode.HASHING_FAILED: {
        "message": "Échec de la génération du token sécurisé",
        "details": "Erreur serveur : impossible de créer le token cryptographique."
    },
    
    ErrorCode.MISSING_IMAGE: {
        "message": "Image manquante",
        "details": "Vous devez fournir une image dans le champ 'image' de la requête."
    },
    
    ErrorCode.MISSING_TOKEN: {
        "message": "Token de référence manquant",
        "details": "Vous devez fournir un token dans le champ 'token_reference' de la requête."
    }
}


def get_error_response(code: ErrorCode) -> Dict[str, Any]:
    """
    Récupère une réponse d'erreur formatée.
    
    Args:
        code: Code d'erreur
    
    Returns:
        Dict formaté avec code, message et détails
    """
    error_info = ERROR_MESSAGES.get(code, {
        "message": "Erreur inconnue",
        "details": "Une erreur inattendue est survenue."
    })
    
    return APIError.format_error(
        code=code,
        message=error_info["message"],
        details=error_info.get("details")
    )