# Import de Pydantic pour définir les structures de données
from pydantic import BaseModel
from typing import List

# --- SCHÉMAS DE RÉPONSE ---

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