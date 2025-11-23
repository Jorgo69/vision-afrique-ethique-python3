# Import des librairies de traitement
import numpy as np
import cv2
import insightface
from typing import List, Optional
from core.config import settings # <-- Importez les paramètres ici

# Variable globale pour l'instance du modèle (le modèle n'a pas besoin d'être régénéré à chaque requête)
INSIGHTFACE_MODEL = None 

# Constantes pour la configuration du modèle InsightFace
MODEL_NAME = 'buffalo_l' # Modèle léger et performant
ALLOWED_MODULES = ['detection', 'genderage', 'recognition']
CONTEXT_ID = -1 # -1 force l'utilisation du CPU

def load_insightface_model() -> None:
    """
    Charge le modèle InsightFace en mémoire globalement.
    Cette fonction est appelée une seule fois au démarrage de l'API.
    """
    global INSIGHTFACE_MODEL
    
    if INSIGHTFACE_MODEL is not None:
        # Si déjà chargé, on sort
        return
        
    print("⏳ Démarrage : Chargement du modèle InsightFace...")
    try:
        # 1. Initialisation de l'analyse faciale
        INSIGHTFACE_MODEL = insightface.app.FaceAnalysis(
            name=MODEL_NAME, 
            allowed_modules=ALLOWED_MODULES
        )
        
        # 2. Préparation du modèle (téléchargement des poids si nécessaire et initialisation)
        # ctx_id=-1 force l'utilisation CPU.
        INSIGHTFACE_MODEL.prepare(ctx_id=CONTEXT_ID, det_size=(640, 640))
        
        print("✅ Modèle InsightFace chargé avec succès.")
    
    except Exception as e:
        print(f"❌ Erreur critique lors du chargement du modèle : {e}")
        # On relance l'erreur pour empêcher l'API de démarrer si le service clé est manquant
        raise RuntimeError("Échec du chargement du modèle InsightFace.")

# --- LA FONCTION CLÉ DU SERVICE ---

def extract_features_from_image(image_bytes: bytes) -> Optional[dict]:
    """
    Fonction principale du service.
    Input: Les bytes de l'image.
    Output: Dictionnaire des features extraites ou None si aucun visage.
    """
    # 1. Vérification que le modèle est chargé
    if INSIGHTFACE_MODEL is None:
        raise RuntimeError("Le modèle InsightFace n'est pas initialisé.")

    # Conversion des bytes en tableau numpy
    np_img = np.frombuffer(image_bytes, dtype=np.uint8) 
    
    # Décodage OpenCV : convertit le format image (JPEG/PNG) en matrice de pixels
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # 2. Détection, alignement, et extraction des features
    # INSIGHTFACE_MODEL.get() : C'est le cœur du traitement.
    faces = INSIGHTFACE_MODEL.get(img)

    # 3. Traitement du résultat
    if not faces:
        # Aucun visage détecté, on retourne None
        return None
    
    # On prend le premier visage détecté (le plus grand ou le plus central)
    face = faces[0] 

    # 4. Construction du dictionnaire de features
    # WARNING: face.embedding est la donnée biométrique brute.
    return {
        "age": int(face.age), # Âge estimé, converti en int standard
        "gender": 'F' if face.gender == 1 else 'M', # Genre estimé (1=F, 0=M)
        "embedding": face.embedding.tolist() # Vecteur de 512 caractéristiques
    }