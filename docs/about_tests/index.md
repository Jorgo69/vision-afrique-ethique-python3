Parfait ! On y va étape par étape, très clairement. 🚀

## Étape 1 : Installation de Pytest 📦

Ouvrez votre terminal, activez votre environnement virtuel et installez :

```bash
cd ~/Bureau/Bureau-HorsBureau/Bureau/Python/FastApi/vision-afrique-ethique
source venv/bin/activate
pip install pytest pytest-asyncio httpx
```

**Explication :**
- `pytest` : Framework de tests
- `pytest-asyncio` : Pour tester les fonctions async de FastAPI
- `httpx` : Client HTTP pour tester l'API (comme requests mais async)

**Vérifiez l'installation :**
```bash
pytest --version
```

Vous devriez voir : `pytest 8.x.x`

---

## Étape 2 : Créer la Structure des Tests 📁

Dans la racine de votre projet, créez le dossier `tests/` :

```bash
mkdir tests
cd tests
```

**Créez ces fichiers vides pour l'instant :**

```bash
touch __init__.py
touch conftest.py
touch test_health.py
```

**Votre structure devient :**
```
vision-afrique-ethique/
├── api/
├── core/
├── services/
├── tests/              # ✅ NOUVEAU
│   ├── __init__.py
│   ├── conftest.py
│   └── test_health.py
├── app.py
├── security.py
└── ...
```

---

## Étape 3 : Configuration Pytest (`pytest.ini`) ⚙️

Retournez à la racine du projet :

```bash
cd ..
```

Créez le fichier `pytest.ini` :

```bash
nano pytest.ini
```

Collez ce contenu :

```ini
[pytest]
# Dossier où chercher les tests
testpaths = tests

# Options par défaut
addopts = 
    -v                    # Verbose (affiche les détails)
    --tb=short           # Traceback court en cas d'erreur
    --strict-markers     # Erreur si marker inconnu
    -p no:warnings       # Masquer les warnings (optionnel)

# Markers personnalisés (pour organiser les tests)
markers =
    slow: Tests lents (ex: tests de performance)
    integration: Tests d'intégration (testent plusieurs composants)
    unit: Tests unitaires (testent une fonction isolée)

# Configuration asyncio pour FastAPI
asyncio_mode = auto
```

**Sauvegardez** (`Ctrl+O`, `Entrée`, `Ctrl+X`)

---

## Étape 4 : Configuration Commune (`conftest.py`) 🔧

Ce fichier contient le code partagé par tous les tests.

Ouvrez `tests/conftest.py` :

```bash
nano tests/conftest.py
```

Collez ce contenu :

```python
"""
Configuration commune pour tous les tests.
Ce fichier est automatiquement chargé par pytest.
"""

import pytest
from fastapi.testclient import TestClient
from app import app

# ============================================
# FIXTURE : Client de Test
# ============================================

@pytest.fixture
def client():
    """
    Crée un client de test pour appeler l'API.
    Cette fixture est réutilisable dans tous les tests.
    
    Utilisation dans un test :
        def test_exemple(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    return TestClient(app)


# ============================================
# FIXTURE : Chemin vers une Image de Test
# ============================================

@pytest.fixture
def sample_image_path():
    """
    Retourne le chemin vers une image de test valide.
    
    IMPORTANT : Créez le dossier tests/fixtures/ et mettez-y une image.
    """
    return "tests/fixtures/test_face.jpg"


@pytest.fixture
def sample_image_bytes(sample_image_path):
    """
    Lit et retourne les bytes d'une image de test.
    """
    with open(sample_image_path, "rb") as f:
        return f.read()


# ============================================
# FIXTURE : Images Invalides
# ============================================

@pytest.fixture
def invalid_image_bytes():
    """
    Retourne des bytes qui ne sont pas une image valide.
    """
    return b"Ceci n'est pas une image valide"


@pytest.fixture
def empty_image_bytes():
    """
    Retourne des bytes vides.
    """
    return b""
```

**Sauvegardez**

**Explication :**
- `@pytest.fixture` = Fonction réutilisable dans les tests
- `client` = Permet de faire des requêtes HTTP à l'API sans la démarrer
- `sample_image_path` = Chemin vers une vraie image pour tester
- `invalid_image_bytes` = Données invalides pour tester les erreurs

---

## Étape 5 : Créer le Dossier d'Images de Test 🖼️

Créez un dossier pour les images de test :

```bash
mkdir -p tests/fixtures
```

**Copiez votre image de test :**

```bash
cp images/image1.jpg tests/fixtures/test_face.jpg
```

**Vérifiez :**
```bash
ls tests/fixtures/
```

Vous devriez voir : `test_face.jpg`

---

## Étape 6 : Premier Test Simple (`test_health.py`) ✅

Ouvrez `tests/test_health.py` :

```bash
nano tests/test_health.py
```

Collez ce contenu :

```python
"""
Tests pour les endpoints de santé de l'API.
Ces tests vérifient que l'API démarre correctement.
"""

import pytest

# ============================================
# TEST 1 : Endpoint racine "/"
# ============================================

def test_root_endpoint(client):
    """
    Teste que l'endpoint racine répond correctement.
    
    Attend :
    - Status 200
    - Un message JSON
    """
    response = client.get("/")
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "API" in data["message"]


# ============================================
# TEST 2 : Endpoint /health
# ============================================

def test_health_endpoint(client):
    """
    Teste que l'endpoint /health répond correctement.
    
    Attend :
    - Status 200
    - model_loaded = True
    """
    response = client.get("/health")
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] == True
    assert "version" in data
```

**Sauvegardez**

---

## Étape 7 : Lancer les Tests 🎯

Retournez à la racine et lancez pytest :

```bash
cd ~/Bureau/Bureau-HorsBureau/Bureau/Python/FastApi/vision-afrique-ethique
pytest
```

**Vous devriez voir :**

```
======================== test session starts ========================
platform linux -- Python 3.12.x, pytest-8.x.x, pluggy-1.x.x
rootdir: /home/.../vision-afrique-ethique
configfile: pytest.ini
testpaths: tests
collected 2 items

tests/test_health.py ✓✓                                      [100%]

========================= 2 passed in 1.23s =========================
```

🎉 **Félicitations ! Vos premiers tests passent !**

---

## Étape 8 : Test d'Extraction de Features 🧪

Créez `tests/test_extraction.py` :

```bash
nano tests/test_extraction.py
```

Collez ce contenu :

```python
"""
Tests pour l'endpoint /face/extract
Vérifie l'extraction de features faciales.
"""

import pytest

# ============================================
# TEST 1 : Extraction Réussie
# ============================================

def test_extract_features_success(client, sample_image_path):
    """
    Teste l'extraction avec une image valide contenant un visage.
    
    Attend :
    - Status 200
    - Âge, genre, embedding présents
    """
    with open(sample_image_path, "rb") as f:
        response = client.post(
            "/face/extract",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "age" in data
    assert "gender" in data
    assert "embedding" in data
    
    # Vérifications de type
    assert isinstance(data["age"], int)
    assert data["gender"] in ["M", "F"]
    assert isinstance(data["embedding"], list)
    assert len(data["embedding"]) == 512  # InsightFace = 512 dimensions


# ============================================
# TEST 2 : Image Invalide
# ============================================

def test_extract_features_invalid_image(client, invalid_image_bytes):
    """
    Teste avec des données qui ne sont pas une image.
    
    Attend :
    - Status 400 ou 500
    - Message d'erreur clair
    """
    response = client.post(
        "/face/extract",
        files={"image": ("test.jpg", invalid_image_bytes, "image/jpeg")}
    )
    
    # Devrait échouer
    assert response.status_code in [400, 500]
    data = response.json()
    assert "detail" in data


# ============================================
# TEST 3 : Fichier Vide
# ============================================

def test_extract_features_empty_file(client, empty_image_bytes):
    """
    Teste avec un fichier vide.
    
    Attend :
    - Status 400 ou 500
    """
    response = client.post(
        "/face/extract",
        files={"image": ("test.jpg", empty_image_bytes, "image/jpeg")}
    )
    
    assert response.status_code in [400, 500]


# ============================================
# TEST 4 : Pas de Fichier Envoyé
# ============================================

def test_extract_features_no_file(client):
    """
    Teste sans envoyer de fichier.
    
    Attend :
    - Status 422 (Validation Error)
    """
    response = client.post("/face/extract")
    
    assert response.status_code == 422
```

**Sauvegardez**

---

## Étape 9 : Lancer Tous les Tests 🚀

```bash
pytest
```

**Résultat attendu :**

```
tests/test_extraction.py ✓✓✗✗                               [60%]
tests/test_health.py ✓✓                                      [100%]

================ 4 passed, 2 failed in 2.34s ==================
```

**C'est NORMAL que certains tests échouent !** 🎯

---

## Étape 10 : Analyser les Échecs 🔍

Pytest vous montre **exactement** ce qui ne va pas :

```
FAILED tests/test_extraction.py::test_extract_features_invalid_image
FAILED tests/test_extraction.py::test_extract_features_empty_file
```

**Ces échecs nous révèlent :**
1. L'API ne gère pas bien les images invalides
2. Le message d'erreur n'est pas clair
3. Il faut améliorer la validation

---

## Résumé de ce qu'on a fait ✅

1. ✅ Installé pytest
2. ✅ Créé la structure `tests/`
3. ✅ Configuré `pytest.ini`
4. ✅ Créé `conftest.py` (fixtures réutilisables)
5. ✅ Créé `test_health.py` (tests basiques qui passent)
6. ✅ Créé `test_extraction.py` (tests qui révèlent des problèmes)
7. ✅ **Découvert des bugs à corriger !**

---

## Prochaine Étape 🎯

Maintenant qu'on a des tests qui **révèlent les problèmes**, on va :

1. **Corriger le code** pour que tous les tests passent
2. **Ajouter plus de tests** (tokenization, matching)
3. **Atteindre 100% de tests verts** ✅

**Voulez-vous qu'on corrige maintenant les bugs révélés par les tests ?**

Ou préférez-vous d'abord créer tous les autres fichiers de tests (`test_tokenization.py`, `test_matching.py`) ?

Dites-moi et on continue ! 💪