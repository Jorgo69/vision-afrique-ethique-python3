"""
Schémas Pydantic pour la validation et documentation des données.
"""

from pydantic import BaseModel, Field
from typing import List

# --- SCHÉMAS DE RÉPONSE ---

class FaceExtractionResponse(BaseModel):
    """
    Réponse de l'endpoint /face/extract
    """
    status: str = Field(
        default="success",
        description="Statut de la requête"
    )
    age: int = Field(
        ...,
        description="Âge estimé de la personne (en années)",
        example=24,
        ge=0,
        le=120
    )
    gender: str = Field(
        ...,
        description="Genre estimé : 'M' (Masculin) ou 'F' (Féminin)",
        example="M",
        pattern="^[MF]$"
    )
    embedding: List[float] = Field(
        ...,
        description="Vecteur biométrique de 512 dimensions (représentation numérique unique du visage)",
        min_length=512,
        max_length=512
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "age": 24,
                "gender": "M",
                "embedding": [
                    -0.088, 1.089, 0.140, 0.012, 1.767,
                    # ... 507 valeurs supplémentaires
                ]
            }
        }


class TokenizeResponse(BaseModel):
    """
    Réponse de l'endpoint /face/tokenize
    """
    status: str = Field(
        default="success",
        description="Statut de la requête"
    )
    age: int = Field(
        ...,
        description="Âge estimé (métadonnée)",
        example=24
    )
    gender: str = Field(
        ...,
        description="Genre estimé (métadonnée)",
        example="M"
    )
    token: str = Field(
        ...,
        description="Token cryptographique Argon2 (irréversible, sécurisé pour stockage BDD)",
        example="$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJl...",
        min_length=50
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "age": 24,
                "gender": "M",
                "token": "$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJlX2NoYWluZQ$+Ag6nAszhHAb9GObNNHmtayySFARMFvOx7vaOOabulY"
            }
        }


class MatchResponse(BaseModel):
    """
    Réponse de l'endpoint /face/match
    """
    status: str = Field(
        default="success",
        description="Statut de la requête"
    )
    match_found: bool = Field(
        ...,
        description="True si le visage correspond au token, False sinon"
    )
    detail: str = Field(
        ...,
        description="Message explicatif du résultat"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "Correspondance trouvée",
                    "value": {
                        "status": "success",
                        "match_found": True,
                        "detail": "Correspondance d'identité vérifiée avec succès."
                    }
                },
                {
                    "summary": "Pas de correspondance",
                    "value": {
                        "status": "success",
                        "match_found": False,
                        "detail": "Le visage ne correspond pas au token de référence."
                    }
                }
            ]
        }