"""
Tests pour l'endpoint /face/tokenize
Vérifie la génération de tokens sécurisés.
"""

import pytest

# ============================================
# TEST 1 : Tokenization Réussie
# ============================================

@pytest.mark.asyncio
async def test_tokenize_success(client, sample_image_path):
    """
    Teste la génération de token avec une image valide.
    
    Attend :
    - Status 200
    - Token Argon2 généré
    - Âge et genre présents
    - PAS d'embedding brut
    """
    with open(sample_image_path, "rb") as f:
        response = await client.post(
            "/face/tokenize",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "age" in data
    assert "gender" in data
    assert "token" in data
    
    # Vérifier le format du token Argon2
    assert data["token"].startswith("$argon2id$")
    assert len(data["token"]) > 50  # Token Argon2 est long
    
    # S'assurer qu'il n'y a PAS d'embedding dans la réponse (sécurité)
    assert "embedding" not in data
    
    # Vérifications de type
    assert isinstance(data["age"], int)
    assert data["gender"] in ["M", "F"]


# ============================================
# TEST 2 : Token Unique par Image
# ============================================

@pytest.mark.asyncio
async def test_tokenize_deterministic(client, sample_image_path):
    """
    Teste que la même image génère toujours le même token.
    (Déterminisme du hachage)
    """
    # Premier appel
    with open(sample_image_path, "rb") as f:
        response1 = await client.post(
            "/face/tokenize",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    token1 = response1.json()["token"]
    
    # Deuxième appel avec la même image
    with open(sample_image_path, "rb") as f:
        response2 = await client.post(
            "/face/tokenize",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    token2 = response2.json()["token"]
    
    # Les tokens doivent être identiques (même image = même hash)
    assert token1 == token2


# ============================================
# TEST 3 : Tokenization sans Visage
# ============================================

@pytest.mark.asyncio
async def test_tokenize_no_face(client, invalid_image_bytes):
    """
    Teste avec une image sans visage détectable.
    
    Attend :
    - Status 400 (Bad Request)
    - Message d'erreur clair
    """
    response = await client.post(
        "/face/tokenize",
        files={"image": ("test.jpg", invalid_image_bytes, "image/jpeg")}
    )
    
    assert response.status_code == 400
    data = response.json()
    
    # ✅ Nouveau format structuré
    assert "detail" in data
    assert "error" in data["detail"]
    
    error = data["detail"]["error"]
    assert error["code"] in ["IMAGE_CORRUPTED", "NO_FACE_DETECTED"]
    
    # Vérifier que le message mentionne le problème
    message_lower = error["message"].lower()
    assert "image" in message_lower or "visage" in message_lower


# ============================================
# TEST 4 : Tokenization sans Fichier
# ============================================

@pytest.mark.asyncio
async def test_tokenize_no_file(client):
    """
    Teste sans envoyer de fichier.
    
    Attend :
    - Status 422 (Validation Error)
    """
    response = await client.post("/face/tokenize")
    
    assert response.status_code == 422