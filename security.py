# Import des bibliothèques de sécurité et de configuration

# hashlib pour les fonctions de hachage standard (comme SHA-256)
import hashlib
# os pour les opérations basiques (non strictement nécessaire ici mais bonne pratique)
import os
# typing pour les annotations de type
from typing import List, Union

# argon2 pour le hachage coûteux en ressources (résistant à la force brute)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError 
from argon2.low_level import hash_secret, verify_secret, Type  # ✅ AJOUTÉ

# numpy pour manipuler l'embedding (vecteur de floats)
import numpy as np

# Importation des paramètres de sécurité depuis la configuration centrale
from core.config import settings 

# Initialisation de l'instance Argon2
# C'est l'équivalent de définir les coûts (mémoire, temps, parallélisme) pour le hachage.
# Ces paramètres peuvent être ajustés en fonction de la performance requise.
ph = PasswordHasher(
    time_cost=2,        # Nombre d'itérations
    memory_cost=65536,  # Utilisation mémoire (kibibytes)
    parallelism=4       # Degré de parallélisme (nombre de threads)
)

# --- FONCTION CLÉ : DOUBLE HACHAGE ---

def hash_embedding(embedding: List[float]) -> str:
    """
    Applique un double hachage irréversible et salé à l'embedding biométrique.
    
    Étape 1: Hachage rapide (SHA-256) du vecteur pour le convertir en une chaîne
             de bytes unique et reproductible.
    Étape 2: Hachage lent (Argon2) du résultat en utilisant les secrets du projet
             comme "sel" renforcé.
             
    Input: Liste des 512 floats (l'embedding biométrique).
    Output: Chaîne de caractères représentant le token cryptographique (irréversible).
    """
    
    # --- 1. Préparation de la donnée brute (Hash initial reproductible) ---
    
    # 1.1 Convertir l'embedding List[float] en array numpy (nécessaire pour tobytes())
    embedding_array = np.array(embedding, dtype=np.float32)
    
    # 1.2 Sérialiser l'array numpy en bytes
    # Les embeddings doivent TOUJOURS être sérialisés de manière standard (ex: little-endian)
    embedding_bytes = embedding_array.tobytes(order='C') 

    # 1.3 Hashage rapide (SHA-256)
    # On applique un premier hash simple sur les bytes de l'embedding.
    # Ceci garantit que même une micro-variation dans l'embedding donne un input Argone2 complètement différent.
    sha256_hash = hashlib.sha256(embedding_bytes).hexdigest()
    
    # --- 2. Renforcement du Hachage (Argon2) avec les Secrets (Double Hashage) ---
    
    # 2.1 Concaténation du hash SHA-256 avec le premier secret
    # C'est une méthode de "salage" simple mais efficace pour les tokens biométriques.
    # Le SECRET_PART1 est utilisé comme "mot de passe" pour Argon2 (Argon2 est conçu pour les mots de passe)
    input_for_argon = sha256_hash + settings.VISION_SECRET_PART1
    
    # 2.2 Hachage Argon2 (le hachage lent et sécurisé)
    # Le SECRET_PART2 est utilisé comme un sel statique supplémentaire pour renforcer.
    # WARNING: Le sel pour Argon2 devrait idéalement être unique par utilisateur. 
    # Ici, nous utilisons SECRET_PART2 pour une "clé statique forte".
    try:
        # encode(encoding='utf-8') convertit la chaîne en bytes, obligatoire pour Argon2
        # Le 'salt' ici est le secret statique, le 'password' est la concaténation SHA + Secret1
        token_argon2 = hash_secret(
            secret=input_for_argon.encode('utf-8'),
            salt=settings.VISION_SECRET_PART2.encode('utf-8')[:16],  # Argon2 nécessite exactement 16 bytes
            time_cost=2,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID  # Argon2id
        )
        
        # Le résultat est une chaîne de caractères formatée ($argon2id$...)
        return token_argon2

    except Exception as e:
        # Gestion des erreurs (ex: secrets trop courts, problème de mémoire, etc.)
        print(f"Erreur de hachage Argon2: {e}")
        raise RuntimeError("Échec de la génération du token sécurisé.")

# --- FONCTION DE VÉRIFICATION (POUR PHASE 3) ---

# Cette fonction ne sera utilisée qu'en Phase 3 (Job Match)
def verify_token(embedding: List[float], hashed_token: str) -> bool:
    """
    Vérifie si un embedding brut correspond à un token Argon2 haché.
    (NON REQUIS POUR LA PHASE 2, MAIS PRÊT POUR LA PHASE 3)
    """
    # 1. Régénérer l'input SHA-256 du nouvel embedding
    embedding_array = np.array(embedding, dtype=np.float32)
    embedding_bytes = embedding_array.tobytes(order='C') 
    sha256_hash = hashlib.sha256(embedding_bytes).hexdigest()
    
    # 2. Régénérer l'input Argon2
    input_for_argon = sha256_hash + settings.VISION_SECRET_PART1
    
    # 3. Vérification Argon2 (utilise la configuration de hachage par défaut)
    try:
        # Cette méthode prend l'input brut et le compare au hash stocké.
        # Elle inclut la logique pour extraire le sel (SECRET_PART2) du hash stocké.
        ph.verify(
            hashed_token, 
            input_for_argon.encode('utf-8')
        )
        return True
    except VerifyMismatchError:
        # Le hachage ne correspond pas
        return False
    except Exception as e:
        # Autre erreur (format, etc.)
        print(f"Erreur de vérification Argon2: {e}")
        return False