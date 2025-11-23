
-----

## 📝 PROGRESS.md : Suivi du Moteur de Vision Éthique

Ce document retrace l'évolution du projet **Vision Afrique Éthique** (API de reconnaissance faciale éthique), en détaillant l'architecture et le statut des phases.

### 1\. 📂 Arborescence du Projet Actuel

L'architecture est basée sur le principe de la **Séparation des Préoccupations (SoC)**, inspirée des frameworks modulaires (NestJS/Laravel), pour garantir l'évolutivité et la maintenabilité.

```
vision-afrique-ethique/
├── api/
│   └── endpoints/
│       └── face.py         # 🗄️ Controller : Gère les requêtes HTTP (POST /extract), validation de l'input, et appelle les Services. Point d'entrée logique.
├── core/
│   ├── config.py           # ⚙️ Configuration : Utilise Pydantic-Settings pour lire et valider les variables d'environnement (.env).
│   └── models.py           # 🧠 Modèles de données : Schémas Pydantic pour définir la structure des requêtes et des réponses (Input/Output).
├── services/
│   └── face_extractor.py   # 💡 Service Métier : Contient la logique métier pure, le chargement du modèle InsightFace et la fonction extract_features.
├── app.py                  # 🚀 Point d'entrée physique : Initialisation de l'application FastAPI et inclusion des APIRouters. Reste minimal.
├── security.py             # 🛡️ Sécurité (À faire) : Contient les fonctions de double hashage cryptographique (Phase 2).
├── requirements.txt        # Liste des dépendances Python requises.
├── .env                    # Variables d'environnement (IGNORÉ par Git).
├── .gitignore              # Liste des fichiers/dossiers à ignorer par Git.
└── README.md
```

**Flot de la Requête POST /face/extract (Point de sortie)** :

1.  **Client** envoie **Image** à `app.py` via la route `/face/extract`.
2.  `app.py` délègue à `api/endpoints/face.py` (`APIRouter`).
3.  `face.py` lit l'image et appelle la fonction dans `services/face_extractor.py`.
4.  `face_extractor.py` utilise InsightFace, extrait les features.
5.  `face_extractor.py` retourne le dictionnaire de features (embedding brut) à `face.py`.
6.  `face.py` utilise `core/models.py` pour valider et sérialiser le dictionnaire en **JSON**.
7.  **Client** reçoit le **JSON** (Statut, Âge, Genre, Embedding).

-----

### 2\. ✅ Progression par Phase

| Phase | Description | Statut | Tâches (To Do) |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Job Extract :** Architecture modulaire, chargement du modèle InsightFace (CPU), et endpoint `/face/extract` (Age, Gender, Embedding brut). | **Terminée** | [ ] Finaliser l'intégration de `core/config.py` dans `face.py` (facultatif pour le moment). |
| **Phase 2** | **Job Tokenize :** Sécurité de base, implémentation du **double hashage** cryptographique des embeddings. | **En Cours** | [ ] Implémenter les fonctions de hashage dans `security.py`.<br>[ ] Créer l'endpoint `/face/tokenize` (qui appelle `/extract` puis le hashage).<br>[ ] Mettre à jour `face_extractor.py` pour *ne plus* renvoyer l'embedding brut dans `/extract`. |
| **Phase 3** | **Job Match :** Comparaison de tokens, implémentation du score de similarité (API de vérification). | À faire | [ ] Créer l'endpoint `/face/match` (token 1 vs token 2).<br>[ ] Définir la logique de comparaison sécurisée. |
| **Phase 4** | **Packaging :** Conteneurisation (Docker), Documentation API complète (Swagger). | À faire | [ ] Créer le `Dockerfile` et `.dockerignore`.<br>[ ] Déployer un exemple simple. |

-----

### 3\. 🚧 Journal des Tâches / Problèmes (Mise à jour)

| Date | Description / Problème | Résolution |
| :--- | :--- | :--- |
| 2025-11-23 | **Refactorisation Architecturale :** Déplacement de la logique de `app.py` vers les contrôleurs et services. | Migration complète vers la structure modulaire `api/endpoints`, `services`, `core`. |
| 2025-11-23 | **`ImportError`** : `cannot import name 'settings' from 'core.config'` | **Cause :** La librairie `pydantic-settings` n'était pas trouvée par l'interpréteur. **Résolution :** Vérification de l'activation de l'environnement virtuel (`source venv/bin/activate`) et installation de `pip install pydantic-settings`. |
| 2025-11-23 | **Démarrage serveur :** OK. | Le serveur se lance, l'événement `startup` charge le modèle InsightFace. |
| **Aujourd'hui** | **Prochain Objectif :** Démarrer l'implémentation de `security.py` pour la Phase 2. | *En attente de la définition des algorithmes de hashage.* |

-----

### 4\. 🎯 Prochaines Étapes Définies

1.  **Implémentation du Hashage :** Créer la fonction de double hashage irréversible (ex: Scrypt ou Argon2 combiné à SHA-256) dans `security.py`.
2.  **Création du Tokenizer :** Créer l'endpoint `/face/tokenize` qui s'assure que l'embedding brut ne quitte jamais la fonction de traitement sans être transformé en token sécurisé.