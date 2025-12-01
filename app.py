from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Import de la fonction pour charger le modèle
from services.face_extractor import load_insightface_model

# Import du routeur
from api.endpoints import face

# --- GESTION DU LIFECYCLE ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.
    """
    # Startup
    print("🚀 Démarrage : Chargement du modèle InsightFace...")
    load_insightface_model()
    print("✅ Modèle chargé avec succès !")
    
    yield  # L'application tourne ici
    
    # Shutdown
    print("🛑 Arrêt : Nettoyage des ressources...")


# --- INITIALISATION DE L'APPLICATION ---

app = FastAPI(
    title="🌍 FaceAuth API",
    description="""
## API de Reconnaissance Faciale Privacy-First

**FaceAuth** est un moteur de reconnaissance faciale open source conçu pour :

- ✅ **Protéger la vie privée** : Aucun stockage d'images ou d'embeddings bruts
- ✅ **Sécuriser les données** : Tokens cryptographiques Argon2 irréversibles
- ✅ **Faciliter l'intégration** : API REST simple et bien documentée
- ✅ **Open Source** : Code transparent, auditable par tous

---

### 🚀 Démarrage Rapide

**Workflow en 3 étapes :**

1. **Enregistrement** : Tokeniser un visage avec `POST /face/tokenize`
2. **Stockage** : Sauvegarder le token en base de données
3. **Vérification** : Authentifier avec `POST /face/match`

---

### 📖 Documentation

- [Guide API complet](./docs/API.md) - Tous les détails et exemples
- [Guide de contribution](./CONTRIBUTING.md) - Comment contribuer
- [Code source](https://github.com/jorgo69/faceauth-api)

---

### 🔒 Sécurité

⚠️ **Important avant déploiement :**
- Changez les secrets dans `.env`
- Utilisez HTTPS en production
- Activez le rate limiting
- Ne loggez JAMAIS les images

---

### 📞 Support

- **GitHub Issues** : [Signaler un bug](https://github.com/jorgo69/faceauth-api/issues)
- **Email** : support@faceauth.io
- **Discord** : [Rejoindre la communauté](#)
""",
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "FaceAuth Support",
        "url": "https://github.com/jorgo69/faceauth-api",
        "email": "votre.email@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Santé",
            "description": "Endpoints de vérification du statut de l'API"
        },
        {
            "name": "Extraction",
            "description": "Extraction de features biométriques (âge, genre, embedding) et génération de tokens sécurisés"
        }
    ]
)

# Inclusion des routes
app.include_router(face.router)


# --- ROUTES DE SANTÉ ---

@app.get(
    "/",
    tags=["Santé"],
    summary="Vérifier que l'API est en ligne",
    response_description="Message de confirmation"
)
async def root():
    """
    Endpoint racine pour vérifier rapidement que l'API répond.
    
    **Utilisation :**
    ```bash
    curl http://localhost:8000/
    ```
    
    **Réponse attendue :**
    ```json
    {
      "message": "API Vision Afrique Éthique en ligne."
    }
    ```
    """
    return {"message": "API Vision Afrique Éthique en ligne."}


@app.get(
    "/health",
    tags=["Santé"],
    summary="Vérifier l'état détaillé de l'API",
    response_description="Statut détaillé de l'API et de ses dépendances"
)
async def health_check():
    """
    Vérifie l'état de santé de l'API et de ses composants.
    
    **Utilisation :**
    ```bash
    curl http://localhost:8000/health
    ```
    
    **Réponse attendue :**
    ```json
    {
      "status": "healthy",
      "model_loaded": true,
      "version": "1.0.0"
    }
    ```
    
    **Champs :**
    - `status` : `"healthy"` si tout fonctionne, `"unhealthy"` sinon
    - `model_loaded` : `true` si le modèle InsightFace est chargé en mémoire
    - `version` : Version actuelle de l'API
    
    **Codes de statut :**
    - `200` : API opérationnelle
    - `503` : API en maintenance ou modèle non chargé
    """
    from services.face_extractor import INSIGHTFACE_MODEL
    
    return {
        "status": "healthy",
        "model_loaded": INSIGHTFACE_MODEL is not None,
        "version": "1.0.0"
    }


# --- PERSONNALISATION OPENAPI ---

def custom_openapi():
    """
    Personnalise la documentation OpenAPI/Swagger.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="🌍 FaceAuth API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
        contact=app.contact,
        license_info=app.license_info
    )
    
    # Ajouter le schéma d'erreur standard
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "detail": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "example": "NO_FACE_DETECTED",
                                "description": "Code d'erreur unique"
                            },
                            "message": {
                                "type": "string",
                                "example": "Aucun visage détecté dans l'image",
                                "description": "Message principal"
                            },
                            "details": {
                                "type": "string",
                                "example": "Assurez-vous que le visage est visible...",
                                "description": "Détails et recommandations"
                            }
                        },
                        "required": ["code", "message"]
                    }
                },
                "required": ["error"]
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi