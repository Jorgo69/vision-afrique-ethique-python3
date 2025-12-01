# Import de BaseSettings et Field pour la gestion des variables d'environnement
# (Dans les versions récentes de Pydantic, BaseSettings est déplacé dans pydantic-settings)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Installation nécessaire si vous ne l'avez pas déjà :
# pip install pydantic-settings

class Settings(BaseSettings):
    """
    Classe Pydantic pour lire et valider les variables d'environnement.
    Elle charge automatiquement les variables depuis le fichier .env (grâce à SettingsConfigDict).
    """

    # --- Secrets du projet ---
    # Ces valeurs sont lues depuis le fichier .env ou les variables d'environnement système.
    # Field(min_length=32) assure une validation minimale de la longueur.
    
    # VISION_SECRET_PART1: str = Field(..., min_length=32)
    # VISION_SECRET_PART2: str = Field(..., min_length=32)
    
    # Secrets (obligatoires en production, optionnels en dev)
    VISION_SECRET_PART1: str = Field(default="dev_secret_part1_minimum_32_chars_long")
    VISION_SECRET_PART2: str = Field(default="dev_secret_part2_minimum_32_chars_long")
    
    # --- Configuration du modèle ---
    # Même si elles sont statiques, les mettre ici rend la configuration centrale.
    MODEL_NAME: str = "buffalo_l"
    MODEL_CONTEXT_ID: int = -1  # -1 pour CPU
    
    # Nouvelle : Environnement
    ENVIRONMENT: str = Field(default="development")
    
    # Configuration du modèle Pydantic pour la lecture des fichiers
    model_config = SettingsConfigDict(
        env_file=".env",            # Indique de charger les variables depuis .env
        env_file_encoding='utf-8',  # Encodage
        extra='ignore'              # Ignore les variables non définies ici
    )

# Création de l'instance 'settings' qui sera importée dans toute l'application
settings = Settings()