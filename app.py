# Import des modules nécessaires

# FastAPI est le framework principal pour construire l'API REST
from fastapi import FastAPI, UploadFile, File, HTTPException
# Response est utilisé pour retourner des codes HTTP spécifiques (comme 400)
from fastapi.responses import JSONResponse
# Permet à FastAPI de gérer les données de formulaire (comme le fichier image)
from typing import List, Dict, Any 

# Permet de charger les variables d'environnement depuis le fichier .env
from dotenv import load_dotenv 
import os

# numpy est essentiel pour les opérations sur les tableaux numériques (manipulation de l'embedding)
import numpy as np
# OpenCV est la bibliothèque de vision par ordinateur pour le décodage et le traitement d'image
import cv2 

# InsightFace est la librairie de reconnaissance faciale qui contient les modèles ML
import insightface
# Permet de vérifier la validité de l'objet Face (sera plus utile en phase 2)
from insightface.app.common import Face 

# --- INITIALISATION GLOBALE ---

# Chargement des secrets depuis .env (NE PAS COMMITER CE FICHIER)
# Cette étape est vitale pour la sécurité, même si les secrets ne sont pas encore utilisés dans /extract
load_dotenv()
# Récupération d'une variable pour s'assurer que .env est bien chargé
VISION_SECRET_PART1 = os.getenv("VISION_SECRET_PART1")

# Création de l'instance de l'application FastAPI
# 'vision_afrique_ethique' est le nom de l'application
app = FastAPI(
    title="Vision Afrique Éthique API",
    description="API de reconnaissance faciale éthique (Phase 1: Extraction)",
    version="1.0.0"
)

# Variable globale pour stocker l'instance du modèle InsightFace.
# Le modèle est coûteux à charger, on ne doit le faire qu'une seule fois au démarrage.
model = None 

# --- FONCTION DE DÉMARRAGE DE L'APPLICATION ---

@app.on_event("startup")
async def load_model():
    """
    Fonction exécutée au démarrage de l'application FastAPI.
    Elle charge le modèle InsightFace en mémoire pour un accès rapide.
    """
    global model # Indique que nous modifions la variable globale 'model'
    
    # Vérification de la présence des secrets de sécurité
    if not VISION_SECRET_PART1:
        # Si le secret manque, l'API ne doit pas démarrer.
        raise RuntimeError("Erreur: VISION_SECRET_PART1 non trouvé. Vérifiez votre fichier .env.")

    try:
        # Initialisation du modèle d'extraction InsightFace
        # allowed_modules=['detection', 'genderage', 'recognition'] demande de charger
        # les modules pour la détection, l'estimation d'âge/genre, et l'extraction de features.
        model = insightface.app.FaceAnalysis(
            name='buffalo_l', # 'buffalo_l' est un modèle performant et léger pour l'extraction
            allowed_modules=['detection', 'genderage', 'recognition']
        )
        
        # Préparation du modèle : Télécharge les poids et les charge.
        # ctx_id=-1 force l'utilisation du CPU (plus compatible), 0 ou >0 pour GPU si disponible.
        # det_size=(640, 640) spécifie la taille d'entrée pour la détection.
        model.prepare(ctx_id=-1, det_size=(640, 640))
        
        print("✅ Modèle InsightFace chargé avec succès.")

    except Exception as e:
        # Gestion des erreurs de chargement (ex: pas de connexion internet pour télécharger les poids)
        print(f"❌ Erreur lors du chargement du modèle InsightFace: {e}")
        # Arrêter le processus si le modèle ne peut pas être chargé
        raise RuntimeError(f"Échec du démarrage de l'API. {e}")


# --- ENDPOINT D'EXTRACTION DE FEATURES (Job Extract) ---

@app.post("/extract", response_model=Dict[str, Any], status_code=200)
async def extract_face_features(
    # Type Hint pour le fichier: UploadFile pour la gestion des données multipart/form-data
    image: UploadFile = File(..., description="Le fichier image du visage à analyser.")
) -> JSONResponse:
    """
    Prend une image, détecte un visage, extrait l'âge, le genre et l'embedding.
    Ne renvoie que les données biométriques et métadonnées.
    Input: Image (multipart/form-data)
    Output: JSON contenant status, age, gender, et embedding (512 features).
    """
    
    # Vérification de l'instance du modèle
    if model is None:
        # Retourne une erreur si le modèle n'est pas prêt (ne devrait pas arriver après le @app.on_event)
        return JSONResponse(status_code=503, content={"status": "error", "message": "Modèle d'analyse non chargé."})

    try:
        # 1. Lecture de l'image
        # Lecture de tout le contenu du fichier image téléversé
        contents = await image.read()
        # Conversion des bytes lus en tableau numpy. Ceci est le format que OpenCV attend.
        np_img = np.frombuffer(contents, dtype=np.uint8) 

        # 2. Décodage de l'image
        # Conversion des bytes HTTP en image au format OpenCV (matrice BGR)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # 3. Détection et extraction
        # model.get() est la méthode principale : elle détecte les visages, puis exécute
        # l'estimation d'âge/genre et l'extraction de l'embedding pour chaque visage trouvé.
        faces: List[Face] = model.get(img)

        # 4. Vérification du nombre de visages
        if not faces:
            # Si la liste est vide, aucun visage n'a été détecté dans l'image
            return JSONResponse(status_code=400, content={"status": "error", "message": "Aucun visage détecté."})
        
        # Dans cette phase 1, on ne traite que le premier visage trouvé pour simplifier
        face = faces[0] 

        # 5. Extraction des données
        
        # Métadonnées non-biométriques : L'âge estimé
        # L'âge est un entier (int)
        extracted_age: int = face.age 
        
        # Métadonnées non-biométriques : Le genre estimé (0 pour Masculin, 1 pour Féminin)
        # On le convertit immédiatement en chaîne pour une meilleure lisibilité dans la réponse JSON
        extracted_gender: str = 'F' if face.gender == 1 else 'M'
        
        # WARNING: Donnée biométrique brute très sensible.
        # L'embedding est le vecteur de 512 nombres représentant mathématiquement le visage.
        # Il ne doit JAMAIS être stocké en clair.
        # tolist() convertit le tableau numpy en liste Python standard pour la sérialisation JSON.
        extracted_embedding: List[float] = face.embedding.tolist() 

        # 6. Renvoi de la réponse structurée
        # La réponse contient les features extraites
        return JSONResponse(
            status_code=200, 
            content={
                "status": "success",
                # On utilise round() pour éviter des erreurs de sérialisation JSON avec des types numpy complexes
                "age": round(extracted_age), 
                "gender": extracted_gender, 
                "embedding": extracted_embedding # Le vecteur de 512 features
            }
        )

    except Exception as e:
        # Gestion générique des erreurs (ex: image corrompue, problème de décodage, etc.)
        print(f"Erreur interne lors de l'extraction: {e}")
        # Retourne une erreur 500 pour indiquer un problème côté serveur
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Erreur interne du serveur: {e}"})

# Le fichier security.py n'est pas requis pour la phase 1, mais est prêt pour la phase 2.
