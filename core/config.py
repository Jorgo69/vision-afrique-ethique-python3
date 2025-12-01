# Import de BaseSettings et Field pour la gestion des variables d'environnement
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Classe Pydantic pour lire et valider les variables d'environnement.
    Optimisée pour les déploiements avec peu de mémoire (ex: Render gratuit).
    
    LAZY LOADING: Le modèle InsightFace n'est chargé qu'au premier appel API,
    pas au démarrage de l'application. Cela économise ~400MB à startup.
    """

    # --- Secrets du projet ---
    VISION_SECRET_PART1: str = Field(default="dev_secret_part1_minimum_32_chars_long")
    VISION_SECRET_PART2: str = Field(default="dev_secret_part2_minimum_32_chars_long")
    
    # --- Configuration du modèle ---
    MODEL_NAME: str = "buffalo_l"
    MODEL_CONTEXT_ID: int = -1  # -1 pour CPU
    
    # --- Environnement ---
    ENVIRONMENT: str = Field(default="development")
    
    # --- OPTIMIZATION: Lazy Loading ---
    # Si True, charge le modèle à la première utilisation (économise 400MB au démarrage)
    # Si False, charge au startup (ancien comportement)
    LAZY_LOAD_MODEL: bool = Field(default=True)
    
    # Configuration du modèle Pydantic pour la lecture des fichiers
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

# Création de l'instance 'settings' qui sera importée dans toute l'application
settings = Settings()