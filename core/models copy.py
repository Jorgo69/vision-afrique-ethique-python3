# Import de Pydantic pour définir les structures de données
from pydantic import BaseModel
from typing import List


# --- SCHÉMAS DE RÉPONSE ---

# (FaceExtractionResponse existant)
# Définit le format standard de la réponse après extraction
class FaceExtractionResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse JSON de l'endpoint /extract.
    Permet à FastAPI de valider et documenter la sortie.
    """
    status: str = "success"
    age: int
    gender: str
    # WARNING: L'embedding est la donnée biométrique brute.
    # On le définit comme une liste de floats.
    embedding: List[float]
    
# Nouveau schéma de réponse pour le token
class TokenizeResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse JSON de l'endpoint /tokenize.
    Ne renvoie que les métadonnées et le token cryptographique irréversible.
    """
    status: str = "success"
    age: int
    gender: str
    token: str  # Le token haché (chaîne Argon2)
    
# Schéma de réponse pour l'opération de Match
class MatchResponse(BaseModel):
    """
    Schéma Pydantic pour la réponse JSON de l'endpoint /match.
    Indique le résultat de la vérification.
    """
    status: str = "success"
    match_found: bool  # True si l'embedding correspond au token
    detail: str        # Message expliquant le résultat