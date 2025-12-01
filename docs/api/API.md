# 📖 Documentation API FaceAuth

> Guide complet des endpoints, paramètres et codes d'erreur

**Version :** 1.0.0  
**Base URL :** `http://localhost:8000` (développement)  
**Format :** JSON  
**Authentification :** Aucune (Phase 1) | API Key (Phase 2)

---

## Table des Matières

1. [Informations Générales](#informations-générales)
2. [Endpoints](#endpoints)
   - [Health Checks](#health-checks)
   - [Extraction](#extraction)
   - [Tokenization](#tokenization)
   - [Matching](#matching)
3. [Codes d'Erreur](#codes-derreur)
4. [Exemples d'Intégration](#exemples-dintégration)
5. [Limites et Quotas](#limites-et-quotas)

---

## Informations Générales

### Format des Réponses

**Succès (2xx) :**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Erreur (4xx, 5xx) :**
```json
{
  "detail": {
    "error": {
      "code": "ERROR_CODE",
      "message": "Message principal",
      "details": "Détails supplémentaires et recommandations"
    }
  }
}
```

### Headers Requis
```http
Content-Type: multipart/form-data
```

### Limites de Sécurité

| Paramètre | Limite |
|-----------|--------|
| Taille max image | 10 MB |
| Formats acceptés | JPEG, PNG, WebP |
| Dimensions minimales | 200x200 pixels |
| Rate limit | 10 req/sec par IP |

---

## Endpoints

### Health Checks

#### GET `/`

Vérifie que l'API est en ligne.

**Requête :**
```bash
curl http://localhost:8000/
```

**Réponse (200 OK) :**
```json
{
  "message": "API Vision Afrique Éthique en ligne."
}
```

---

#### GET `/health`

Vérifie l'état détaillé de l'API.

**Requête :**
```bash
curl http://localhost:8000/health
```

**Réponse (200 OK) :**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**Champs :**
- `status` : `"healthy"` ou `"unhealthy"`
- `model_loaded` : `true` si le modèle InsightFace est chargé
- `version` : Version de l'API

---

### Extraction

#### POST `/face/extract`

Extrait les features biométriques d'un visage : âge, genre et embedding (vecteur 512D).

**⚠️ Attention :** L'embedding brut est retourné. Pour la sécurité, utilisez `/face/tokenize` en production.

##### Paramètres

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `image` | File | ✅ Oui | Image JPEG, PNG ou WebP (max 10MB) |

##### Exemple de Requête

**cURL :**
```bash
curl -X POST "http://localhost:8000/face/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/chemin/vers/photo.jpg"
```

**Python :**
```python
import requests

with open("photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/face/extract",
        files={"image": f}
    )

data = response.json()
print(f"Âge: {data['age']}, Genre: {data['gender']}")
```

**JavaScript (Node.js) :**
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('image', fs.createReadStream('photo.jpg'));

axios.post('http://localhost:8000/face/extract', form, {
  headers: form.getHeaders()
})
.then(response => {
  console.log(response.data);
});
```

**PHP (Laravel) :**
```php
use Illuminate\Support\Facades\Http;

$response = Http::attach(
    'image', 
    file_get_contents(storage_path('photo.jpg')), 
    'photo.jpg'
)->post('http://localhost:8000/face/extract');

$data = $response->json();
```

##### Réponse (200 OK)
```json
{
  "status": "success",
  "age": 24,
  "gender": "M",
  "embedding": [
    -0.08886908739805222,
    1.0893865823745728,
    0.14056840538978577,
    ...
    // 512 valeurs au total
  ]
}
```

**Champs :**
- `status` : `"success"`
- `age` : Âge estimé (entier)
- `gender` : `"M"` (Masculin) ou `"F"` (Féminin)
- `embedding` : Vecteur de 512 floats (représentation biométrique)

##### Codes d'Erreur Possibles

| Code HTTP | Code Erreur | Description |
|-----------|-------------|-------------|
| 400 | `NO_FACE_DETECTED` | Aucun visage dans l'image |
| 400 | `IMAGE_TOO_LARGE` | Image > 10 MB |
| 400 | `IMAGE_CORRUPTED` | Fichier illisible |
| 400 | `INVALID_IMAGE_FORMAT` | Format non supporté |
| 400 | `IMAGE_TOO_SMALL` | Dimensions < 200x200 |
| 422 | `MISSING_IMAGE` | Paramètre `image` manquant |
| 500 | `MODEL_NOT_LOADED` | Modèle non initialisé |
| 500 | `EXTRACTION_FAILED` | Erreur inattendue |

##### Exemple d'Erreur
```json
{
  "detail": {
    "error": {
      "code": "NO_FACE_DETECTED",
      "message": "Aucun visage détecté dans l'image",
      "details": "Assurez-vous que :\n- Le visage est visible et bien cadré\n- L'image est bien éclairée\n- Le visage occupe au moins 20% de l'image"
    }
  }
}
```

---

### Tokenization

#### POST `/face/tokenize`

Génère un token cryptographique sécurisé (Argon2) à partir d'un visage.

**✅ Recommandé pour la production** : Le token est irréversible et peut être stocké en base de données.

##### Paramètres

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `image` | File | ✅ Oui | Image JPEG, PNG ou WebP (max 10MB) |

##### Exemple de Requête

**cURL :**
```bash
curl -X POST "http://localhost:8000/face/tokenize" \
  -F "image=@photo.jpg"
```

**Python :**
```python
import requests

with open("photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/face/tokenize",
        files={"image": f}
    )

token = response.json()["token"]
# Stockez ce token en BDD : users.face_token = token
```

##### Réponse (200 OK)
```json
{
  "status": "success",
  "age": 24,
  "gender": "M",
  "token": "$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJl..."
}
```

**Champs :**
- `status` : `"success"`
- `age` : Âge estimé (métadonnée)
- `gender` : Genre estimé (métadonnée)
- `token` : Token Argon2 (128+ caractères)

**⚠️ Important :**
- L'embedding brut n'est **JAMAIS** retourné
- Le token est **irréversible** (impossible de retrouver l'embedding)
- Le même visage génère **toujours le même token** (déterministe)

##### Codes d'Erreur Possibles

Mêmes codes que `/face/extract` + :

| Code HTTP | Code Erreur | Description |
|-----------|-------------|-------------|
| 500 | `HASHING_FAILED` | Échec génération token |

---

### Matching

#### POST `/face/match`

Vérifie si un visage correspond à un token de référence.

**Cas d'usage :**
- Authentification biométrique
- Vérification d'identité
- Contrôle d'accès

##### Paramètres

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `image` | File | ✅ Oui | Image du visage à vérifier |
| `token_reference` | String | ✅ Oui | Token Argon2 de référence |

##### Exemple de Requête

**cURL :**
```bash
curl -X POST "http://localhost:8000/face/match" \
  -F "image=@photo_verification.jpg" \
  -F "token_reference=\$argon2id\$v=19\$m=65536..."
```

**Python (Workflow Complet) :**
```python
import requests

# Étape 1 : Enregistrement (une seule fois)
with open("selfie_enregistrement.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/face/tokenize",
        files={"image": f}
    )
reference_token = response.json()["token"]

# Stockez reference_token en BDD
# Ex: db.users.update({"id": user_id}, {"face_token": reference_token})

# Étape 2 : Vérification (à chaque authentification)
with open("selfie_verification.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/face/match",
        files={"image": f},
        data={"token_reference": reference_token}
    )

result = response.json()
if result["match_found"]:
    print("✅ Identité vérifiée !")
else:
    print("❌ Identité non vérifiée")
```

**PHP (Laravel) :**
```php
// Récupérer le token depuis la BDD
$user = User::find($userId);
$referenceToken = $user->face_token;

// Vérifier
$response = Http::attach('image', $imageContent, 'selfie.jpg')
    ->post('http://localhost:8000/face/match', [
        'token_reference' => $referenceToken
    ]);

if ($response->json()['match_found']) {
    // Authentification réussie
}
```

##### Réponse (200 OK)

**Match Trouvé :**
```json
{
  "status": "success",
  "match_found": true,
  "detail": "Correspondance d'identité vérifiée avec succès."
}
```

**Pas de Match :**
```json
{
  "status": "success",
  "match_found": false,
  "detail": "Le visage ne correspond pas au token de référence."
}
```

##### Codes d'Erreur Possibles

Mêmes codes que `/face/tokenize` + :

| Code HTTP | Code Erreur | Description |
|-----------|-------------|-------------|
| 400 | `INVALID_TOKEN_FORMAT` | Token mal formé |
| 422 | `MISSING_TOKEN` | Paramètre manquant |

---

## Codes d'Erreur

### Format Standard
```json
{
  "detail": {
    "error": {
      "code": "ERROR_CODE",
      "message": "Message principal",
      "details": "Détails et recommandations"
    }
  }
}
```

### Liste Complète

#### Erreurs d'Image (400)

##### `NO_FACE_DETECTED`

**Message :** "Aucun visage détecté dans l'image"

**Détails :**
```
Assurez-vous que :
- Le visage est visible et bien cadré
- L'image est bien éclairée
- Le visage occupe au moins 20% de l'image
```

**Solutions :**
- Améliorer la qualité de l'image
- Cadrer le visage correctement
- Augmenter la luminosité

---

##### `IMAGE_TOO_LARGE`

**Message :** "Image trop volumineuse"

**Détails :**
```
Taille maximale autorisée : 10 MB.
Compressez l'image ou réduisez sa résolution.
```

**Solutions :**
- Compresser l'image (JPEG qualité 85%)
- Réduire la résolution (1920x1080 max recommandé)

---

##### `IMAGE_CORRUPTED`

**Message :** "Image corrompue ou illisible"

**Détails :**
```
Le fichier ne peut pas être décodé.
Vérifiez que c'est une image valide (JPEG, PNG, WebP).
```

**Solutions :**
- Vérifier l'intégrité du fichier
- Réenregistrer l'image dans un format supporté

---

##### `INVALID_IMAGE_FORMAT`

**Message :** "Format d'image non supporté"

**Détails :**
```
Formats acceptés : JPEG (.jpg, .jpeg), PNG (.png), WebP (.webp)
```

**Solutions :**
- Convertir l'image en JPEG ou PNG

---

##### `IMAGE_TOO_SMALL`

**Message :** "Image trop petite"

**Détails :**
```
Dimensions minimales : 200x200 pixels.
Utilisez une image de meilleure qualité.
```

**Solutions :**
- Utiliser une image de résolution supérieure

---

#### Erreurs de Token (400, 422)

##### `INVALID_TOKEN_FORMAT`

**Message :** "Format de token invalide"

**Détails :**
```
Le token doit être au format Argon2 ($argon2id$...)
```

**Solutions :**
- Vérifier que le token commence par `$argon2id$`
- Utiliser le token exact retourné par `/face/tokenize`

---

##### `TOKEN_VERIFICATION_FAILED`

**Message :** "Échec de la vérification du token"

**Détails :**
```
Le token est valide mais ne correspond pas au visage fourni.
```

**Solutions :**
- Vérifier que le token correspond bien à la personne
- Refaire une photo de meilleure qualité

---

#### Erreurs Serveur (500)

##### `MODEL_NOT_LOADED`

**Message :** "Modèle de reconnaissance faciale non chargé"

**Détails :**
```
Erreur serveur : le service est en cours d'initialisation.
Réessayez dans quelques secondes.
```

**Solutions :**
- Attendre quelques secondes
- Contacter l'administrateur si le problème persiste

---

##### `EXTRACTION_FAILED`

**Message :** "Échec de l'extraction des features"

**Détails :**
```
Une erreur inattendue est survenue pendant le traitement.
```

**Solutions :**
- Réessayer avec une autre image
- Contacter le support si le problème persiste

---

##### `HASHING_FAILED`

**Message :** "Échec de la génération du token sécurisé"

**Détails :**
```
Erreur serveur : impossible de créer le token cryptographique.
```

**Solutions :**
- Contacter l'administrateur

---

## Exemples d'Intégration

### Scénario 1 : Authentification Biométrique

**Backend (Node.js + Express) :**
```javascript
const express = require('express');
const FormData = require('form-data');
const axios = require('axios');
const app = express();

// Enregistrement d'un utilisateur
app.post('/register', upload.single('selfie'), async (req, res) => {
  const form = new FormData();
  form.append('image', req.file.buffer, 'selfie.jpg');
  
  const response = await axios.post(
    'http://localhost:8000/face/tokenize',
    form,
    { headers: form.getHeaders() }
  );
  
  const token = response.data.token;
  
  // Sauvegarder en BDD
  await User.create({
    email: req.body.email,
    face_token: token,
    age: response.data.age,
    gender: response.data.gender
  });
  
  res.json({ success: true });
});

// Connexion d'un utilisateur
app.post('/login', upload.single('selfie'), async (req, res) => {
  const user = await User.findOne({ email: req.body.email });
  
  const form = new FormData();
  form.append('image', req.file.buffer, 'selfie.jpg');
  form.append('token_reference', user.face_token);
  
  const response = await axios.post(
    'http://localhost:8000/face/match',
    form,
    { headers: form.getHeaders() }
  );
  
  if (response.data.match_found) {
    // Créer une session
    req.session.userId = user.id;
    res.json({ success: true, message: 'Authentifié' });
  } else {
    res.status(401).json({ error: 'Identité non vérifiée' });
  }
});
```

---

### Scénario 2 : Widget de Vérification d'Âge

**Frontend (React) :**
```jsx
import { useState } from 'react';

function AgeVerification() {
  const [verified, setVerified] = useState(false);
  
  const handleCapture = async (imageBlob) => {
    const formData = new FormData();
    formData.append('image', imageBlob);
    
    const response = await fetch('http://localhost:8000/face/extract', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (data.age >= 18) {
      setVerified(true);
    } else {
      alert('Vous devez avoir 18 ans ou plus');
    }
  };
  
  return (
    <div>
      {!verified ? (
        <WebcamCapture onCapture={handleCapture} />
      ) : (
        <p>✅ Âge vérifié : accès autorisé</p>
      )}
    </div>
  );
}
```

---

## Limites et Quotas

| Limite | Valeur | Notes |
|--------|--------|-------|
| Requêtes/seconde | 10 | Par IP |
| Taille max image | 10 MB | Compresser si nécessaire |
| Timeout | 30s | Pour traitement |
| Concurrence max | 100 | Connexions simultanées |

---

## Support

**Questions :** ouvrez une issue sur [GitHub](https://github.com/votre-username/faceauth-api/issues)  
**Email :** votre.email@example.com  
**Discord :** [Rejoindre la communauté](#)

---

**Dernière mise à jour :** 30 Novembre 2025