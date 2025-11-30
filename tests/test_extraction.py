"""
Tests pour l'endpoint /face/extract
Vérifie l'extraction de features faciales.
"""

import pytest

# ============================================
# TEST 1 : Extraction Réussie
# ============================================

@pytest.mark.asyncio
async def test_extract_features_success(client, sample_image_path):
    """
    Teste l'extraction avec une image valide contenant un visage.
    """
    with open(sample_image_path, "rb") as f:
        response = await client.post(
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

@pytest.mark.asyncio
async def test_extract_features_invalid_image(client, invalid_image_bytes):
    """
    Teste avec des données qui ne sont pas une image.
    """
    response = await client.post(
        "/face/extract",
        files={"image": ("test.jpg", invalid_image_bytes, "image/jpeg")}
    )
    
    # Devrait échouer
    # assert response.status_code in [400, 500]
    # data = response.json()
    # assert "detail" in data
    assert response.status_code == 400
    data = response.json()
    
    # ✅ Format correct : {"detail": {"error": {"code": "...", "message": "..."}}}
    assert "detail" in data
    assert "error" in data["detail"]
    assert "code" in data["detail"]["error"]
    assert "message" in data["detail"]["error"]
    
    # Le code doit être l'un des deux possibles
    assert data["detail"]["error"]["code"] in ["IMAGE_CORRUPTED", "NO_FACE_DETECTED"]


# ============================================
# TEST 3 : Fichier Vide
# ============================================

@pytest.mark.asyncio
async def test_extract_features_empty_file(client, empty_image_bytes):
    """
    Teste avec un fichier vide.
    """
    response = await client.post(
        "/face/extract",
        files={"image": ("test.jpg", empty_image_bytes, "image/jpeg")}
    )
    
    assert response.status_code in [400, 500]


# ============================================
# TEST 4 : Pas de Fichier Envoyé
# ============================================

@pytest.mark.asyncio
async def test_extract_features_no_file(client):
    """
    Teste sans envoyer de fichier.
    """
    response = await client.post("/face/extract")
    
    assert response.status_code == 422