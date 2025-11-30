# 🌍 FaceAuth API

> **API de reconnaissance faciale open source, sécurisée et privacy-first**
> 
> Construite en Afrique, pour le monde entier.

[![Tests](https://img.shields.io/badge/tests-15%20passed-success)](./tests)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

---

## 🎯 Vision

FaceAuth est un **moteur de reconnaissance faciale** conçu pour être :
- ✅ **Privacy-First** : Aucun stockage d'images ou d'embeddings bruts
- ✅ **Sécurisé** : Tokens cryptographiques irréversibles (Argon2)
- ✅ **Open Source** : Code transparent, auditable par tous
- ✅ **Modulaire** : Architecture propre et extensible
- ✅ **Accessible** : Auto-hébergeable ou via API cloud

---

## 🚀 Démarrage Rapide (5 minutes)

### Prérequis

- Python 3.12+
- 2 GB RAM minimum
- Linux, macOS ou Windows

### Installation
```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/faceauth-api.git
cd faceauth-api

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les secrets
cp .env.example .env
# Éditez .env et changez les secrets

# 5. Lancer l'API
uvicorn app:app --reload
```

🎉 **L'API tourne maintenant sur http://localhost:8000**

📖 **Documentation interactive** : http://localhost:8000/docs

---

## 📋 Cas d'Usage

### 🏦 Paiement Biométrique
Payez sans carte ni téléphone, juste avec votre visage.
```python
import requests

# 1. Enregistrement (une seule fois)
with open("selfie.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/face/tokenize",
        files={"image": f}
    )
token = response.json()["token"]
# Stockez ce token dans votre BDD : users.face_token = token

# 2. Paiement (à chaque fois)
with open("selfie_paiement.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/face/match",
        files={"image": f},
        data={"token_reference": token}
    )

if response.json()["match_found"]:
    print("✅ Paiement autorisé !")
else:
    print("❌ Identité non vérifiée")
```

### 🏥 Dossier Médical
Accédez à votre dossier médical sans carte vitale.

### 🔞 Vérification d'Âge
Widget pour sites web nécessitant une vérification d'âge.

### 🏠 Contrôle d'Accès
Ouvrez votre porte avec votre visage (Raspberry Pi + caméra).

---

## 🔌 Endpoints Principaux

### POST `/face/extract`
Extrait les features biométriques d'un visage.

**Requête :**
```bash
curl -X POST "http://localhost:8000/face/extract" \
  -F "image=@photo.jpg"
```

**Réponse :**
```json
{
  "status": "success",
  "age": 24,
  "gender": "M",
  "embedding": [0.123, -0.456, ...] // 512 dimensions
}
```

---

### POST `/face/tokenize`
Génère un token sécurisé (à stocker en BDD).

**Requête :**
```bash
curl -X POST "http://localhost:8000/face/tokenize" \
  -F "image=@photo.jpg"
```

**Réponse :**
```json
{
  "status": "success",
  "age": 24,
  "gender": "M",
  "token": "$argon2id$v=19$m=65536,t=2,p=4$..."
}
```

⚠️ **L'embedding brut n'est JAMAIS retourné** (sécurité).

---

### POST `/face/match`
Vérifie si un visage correspond à un token.

**Requête :**
```bash
curl -X POST "http://localhost:8000/face/match" \
  -F "image=@photo.jpg" \
  -F "token_reference=$argon2id$v=19$..."
```

**Réponse :**
```json
{
  "status": "success",
  "match_found": true,
  "detail": "Correspondance d'identité vérifiée avec succès."
}
```

---

## 🛡️ Codes d'Erreur

Toutes les erreurs suivent ce format :
```json
{
  "detail": {
    "error": {
      "code": "NO_FACE_DETECTED",
      "message": "Aucun visage détecté dans l'image",
      "details": "Assurez-vous que le visage est visible..."
    }
  }
}
```

### Liste Complète

| Code | Description |
|------|-------------|
| `NO_FACE_DETECTED` | Aucun visage détecté |
| `IMAGE_TOO_LARGE` | Image > 10 MB |
| `IMAGE_CORRUPTED` | Fichier illisible |
| `INVALID_IMAGE_FORMAT` | Format non supporté |
| `IMAGE_TOO_SMALL` | Dimensions < 200x200 |
| `INVALID_TOKEN_FORMAT` | Token mal formé |
| `TOKEN_VERIFICATION_FAILED` | Pas de correspondance |
| `MODEL_NOT_LOADED` | Modèle non initialisé |

📖 [Documentation complète des erreurs](./docs/API.md#codes-derreur)

---

## 🧪 Tests
```bash
# Lancer tous les tests
pytest -v

# Tests avec couverture
pytest --cov=services --cov=api --cov=core

# Tests d'un module spécifique
pytest tests/test_extraction.py -v
```

**Couverture actuelle : 15 tests, 100% passent** ✅

---

## 📁 Architecture
```
faceauth-api/
├── api/
│   └── endpoints/
│       └── face.py           # Routes FastAPI
├── core/
│   ├── config.py             # Configuration
│   ├── models.py             # Schémas Pydantic
│   └── errors.py             # Codes d'erreur
├── services/
│   └── face_extractor.py     # Logique InsightFace
├── tests/
│   ├── test_extraction.py
│   ├── test_tokenization.py
│   ├── test_matching.py
│   └── test_health.py
├── app.py                    # Point d'entrée
├── security.py               # Hachage Argon2
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🐳 Docker
```bash
# Build
docker build -t faceauth-api .

# Run
docker run -p 8000:8000 \
  -e VISION_SECRET_PART1=your_secret_1 \
  -e VISION_SECRET_PART2=your_secret_2 \
  faceauth-api
```

---

## 🔒 Sécurité

### Ce que Nous Faisons

✅ **Hachage Argon2id** : Résistant aux attaques GPU  
✅ **Pas de stockage d'images** : Suppression immédiate après traitement  
✅ **Pas d'embeddings bruts** : Seuls les tokens sont retournés  
✅ **Rate limiting** : Protection contre les abus  
✅ **Validation stricte** : Taille, format, dimensions

### Ce que Vous Devez Faire

⚠️ **Changez les secrets** dans `.env`  
⚠️ **Utilisez HTTPS** en production  
⚠️ **Ne loggez JAMAIS** les images ou embeddings  
⚠️ **Rotez les secrets** régulièrement

---

## 🤝 Contribution

Nous accueillons toutes les contributions !

1. **Fork** le projet
2. **Créez** une branche (`git checkout -b feature/AmazingFeature`)
3. **Committez** (`git commit -m 'Add AmazingFeature'`)
4. **Pushez** (`git push origin feature/AmazingFeature`)
5. **Ouvrez** une Pull Request

📖 [Guide de contribution](./CONTRIBUTING.md)

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](./LICENSE) pour plus de détails.

---

## 👨‍💻 Auteur

**Ibrahim**  
Développeur Full-Stack | Bénin 🇧🇯

- GitHub: [@votre-username](https://github.com/votre-username)
- LinkedIn: [Votre Profil](https://linkedin.com/in/votre-profil)
- Email: votre.email@example.com

---

## 🙏 Remerciements

- [InsightFace](https://github.com/deepinsight/insightface) pour le modèle de reconnaissance
- [FastAPI](https://fastapi.tiangolo.com) pour le framework
- La communauté open source africaine 🌍

---

## 🗺️ Roadmap

- [ ] Détection de vivacité (anti-spoofing)
- [ ] Support GPU (CUDA)
- [ ] API cloud hébergée
- [ ] SDK JavaScript
- [ ] Dashboard d'administration
- [ ] Détection d'émotions
- [ ] Support vidéo

---

**⭐ Si ce projet vous aide, donnez-lui une étoile !**