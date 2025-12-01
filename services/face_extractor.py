"""
Service de reconnaissance faciale avec InsightFace.
OPTIMISÉ POUR RENDER: Lazy loading du modèle pour économiser la RAM au démarrage.
"""

import numpy as np
import cv2
import insightface
from typing import Optional
from core.config import settings
from core.logger import setup_logger

# ============================================
# Configuration globale
# ============================================
logger = setup_logger(__name__)

# Variable globale pour l'instance du modèle
# Le modèle n'est chargé qu'à la première utilisation (lazy loading)
INSIGHTFACE_MODEL = None

# Constantes de configuration
MODEL_NAME = settings.MODEL_NAME
CONTEXT_ID = settings.MODEL_CONTEXT_ID
ALLOWED_MODULES = ['detection', 'genderage', 'recognition']

# ============================================
# Lazy Loading: Charge le modèle au 1er appel
# ============================================
def _get_model():
    """
    Getter privé qui assure que le modèle est chargé avant utilisation.
    
    Utilise le lazy loading: le modèle ne se charge QUE lors du 1er appel API,
    pas au démarrage de l'application. Cela économise ~400MB de RAM au startup.
    
    Sur Render gratuit (512 MB), c'est essentiel pour ne pas être killed.
    """
    global INSIGHTFACE_MODEL
    
    # ✅ Si le modèle est déjà chargé, on le retourne directement
    if INSIGHTFACE_MODEL is not None:
        return INSIGHTFACE_MODEL
    
    # ⏳ Première utilisation: chargement du modèle
    logger.info("⏳ Démarrage : Chargement du modèle InsightFace...")
    
    try:
        # Initialisation et préparation du modèle
        INSIGHTFACE_MODEL = insightface.app.FaceAnalysis(
            name=MODEL_NAME,
            allowed_modules=ALLOWED_MODULES
        )
        
        # Préparation: téléchargement des poids et initialisation
        # ctx_id=-1 force CPU (pas de GPU)
        # det_size=(640, 640) pour détection optimale
        INSIGHTFACE_MODEL.prepare(ctx_id=CONTEXT_ID, det_size=(640, 640))
        
        logger.info("✅ Modèle InsightFace chargé avec succès.")
        return INSIGHTFACE_MODEL
    
    except Exception as e:
        logger.error(f"❌ Erreur critique lors du chargement du modèle : {e}")
        raise RuntimeError(f"Échec du chargement du modèle InsightFace: {str(e)}")


def extract_features_from_image(image_bytes: bytes) -> Optional[dict]:
    """
    Fonction principale du service: extrait les features biométriques d'une image.
    
    Args:
        image_bytes (bytes): Les bytes de l'image (JPEG, PNG, etc.)
    
    Returns:
        dict: {
            "age": int,                    # Âge estimé
            "gender": str ('M' ou 'F'),    # Genre estimé
            "embedding": List[float]       # Vecteur de 512 features
        }
        ou None si aucun visage détecté
    
    Raises:
        ValueError: Si l'image est invalide/corrompue ou trop petite
        RuntimeError: Si le modèle ne peut pas être chargé
    """
    
    # ✅ ÉTAPE 1: Récupérer le modèle (lazy loading s'active ici si nécessaire)
    model = _get_model()
    
    # ✅ ÉTAPE 2: Convertir les bytes en image
    try:
        np_img = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("IMAGE_CORRUPTED")
    
    except Exception as e:
        logger.error(f"Erreur lors du décodage de l'image: {e}")
        raise ValueError("IMAGE_CORRUPTED")
    
    # ✅ ÉTAPE 3: Vérifier que l'image a une taille minimale
    height, width = img.shape[:2]
    if height < 200 or width < 200:
        logger.warning(f"Image trop petite: {width}x{height}")
        raise ValueError("IMAGE_TOO_SMALL")
    
    # ✅ ÉTAPE 4: Détecter les visages et extraire les features
    try:
        faces = model.get(img)
    except Exception as e:
        logger.error(f"Erreur lors de la détection faciale: {e}")
        raise RuntimeError("FACE_DETECTION_FAILED")
    
    # ✅ ÉTAPE 5: Traiter le résultat
    if not faces:
        # Aucun visage détecté
        logger.info("Aucun visage détecté dans l'image")
        return None
    
    # Prendre le premier visage (le plus grand ou le plus central)
    face = faces[0]
    
    # ✅ ÉTAPE 6: Construire et retourner le dictionnaire de features
    features = {
        "age": int(face.age),                    # Âge estimé
        "gender": 'M' if face.gender == 1 else 'F',  # Genre (1=M, 0=F)
        "embedding": face.embedding.tolist()    # Vecteur 512D
    }
    
    logger.info(f"Features extraites: âge={features['age']}, genre={features['gender']}")
    return features


# ============================================
# Fonction d'initialisation (optionnelle, appelée au startup)
# ============================================
def preload_model() -> None:
    """
    Pré-charge le modèle au démarrage de l'application (optionnel).
    
    Utilise settings.LAZY_LOAD_MODEL:
    - Si True: ne fait rien (lazy loading activé)
    - Si False: charge le modèle immédiatement (ancien comportement)
    """
    if settings.LAZY_LOAD_MODEL:
        logger.info("Lazy loading activé: le modèle sera chargé à la première utilisation")
    else:
        logger.info("Chargement immédiat du modèle au startup...")
        _get_model()