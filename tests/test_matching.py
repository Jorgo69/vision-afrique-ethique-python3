"""
Tests pour l'endpoint /face/match
Vérifie la correspondance entre visages et tokens.
"""

import pytest

# ============================================
# TEST 1 : Match Réussi (Même Personne)
# ============================================

@pytest.mark.asyncio
async def test_match_same_person(client, sample_image_path):
    """
    Teste qu'une image matche avec son propre token.
    
    Scénario :
    1. Générer un token depuis l'image
    2. Vérifier que l'image matche avec ce token
    """
    # Étape 1 : Générer le token
    with open(sample_image_path, "rb") as f:
        tokenize_response = await client.post(
            "/face/tokenize",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    
    assert tokenize_response.status_code == 200
    token = tokenize_response.json()["token"]
    
    # Étape 2 : Vérifier le match
    with open(sample_image_path, "rb") as f:
        match_response = await client.post(
            "/face/match",
            files={"image": ("test.jpg", f, "image/jpeg")},
            data={"token_reference": token}
        )
    
    # Vérifications
    assert match_response.status_code == 200
    data = match_response.json()
    
    assert data["status"] == "success"
    assert data["match_found"] == True
    assert "Correspondance" in data["detail"] or "vérifiée" in data["detail"]


# ============================================
# TEST 2 : Match Échoue (Token Invalide)
# ============================================

@pytest.mark.asyncio
async def test_match_invalid_token(client, sample_image_path):
    """
    Teste avec un token invalide (mauvais format).
    
    Attend :
    - Status 422 ou 400
    - Message d'erreur clair
    """
    fake_token = "invalid_token_format"
    
    with open(sample_image_path, "rb") as f:
        response = await client.post(
            "/face/match",
            files={"image": ("test.jpg", f, "image/jpeg")},
            data={"token_reference": fake_token}
        )
    
    # Devrait rejeter le token invalide
    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data


# ============================================
# TEST 3 : Match sans Token
# ============================================

@pytest.mark.asyncio
async def test_match_no_token(client, sample_image_path):
    """
    Teste sans fournir de token_reference.
    
    Attend :
    - Status 422 (Validation Error)
    """
    with open(sample_image_path, "rb") as f:
        response = await client.post(
            "/face/match",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 422


# ============================================
# TEST 4 : Match sans Image
# ============================================

@pytest.mark.asyncio
async def test_match_no_image(client):
    """
    Teste sans fournir d'image.
    
    Attend :
    - Status 422 (Validation Error)
    """
    fake_token = "$argon2id$v=19$m=65536,t=2,p=4$test"
    
    response = await client.post(
        "/face/match",
        data={"token_reference": fake_token}
    )
    
    assert response.status_code == 422


# ============================================
# TEST 5 : Match avec Image sans Visage
# ============================================

@pytest.mark.asyncio
async def test_match_no_face_in_image(client, invalid_image_bytes):
    """
    Teste avec une image sans visage détectable.
    
    Attend :
    - Status 400
    - Message d'erreur clair
    """
    fake_token = "$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJl"
    
    response = await client.post(
        "/face/match",
        files={"image": ("test.jpg", invalid_image_bytes, "image/jpeg")},
        data={"token_reference": fake_token}
    )
    
    assert response.status_code == 400
    data = response.json()
    # ✅ Nouveau format structuré
    assert "detail" in data
    assert "error" in data["detail"]
    
    error = data["detail"]["error"]
    assert error["code"] in ["IMAGE_CORRUPTED", "NO_FACE_DETECTED"]
    
    # Vérifier que le message est clair
    message_lower = error["message"].lower()
    assert "image" in message_lower or "visage" in message_lower