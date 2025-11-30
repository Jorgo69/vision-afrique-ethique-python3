"""
Tests pour les endpoints de santé de l'API.
Ces tests vérifient que l'API démarre correctement.
"""

import pytest

# ============================================
# TEST 1 : Endpoint racine "/"
# ============================================

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """
    Teste que l'endpoint racine répond correctement.
    
    Attend :
    - Status 200
    - Un message JSON
    """
    response = await client.get("/")
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "API" in data["message"]


# ============================================
# TEST 2 : Endpoint /health
# ============================================

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """
    Teste que l'endpoint /health répond correctement.
    
    Attend :
    - Status 200
    - model_loaded = True (ou la valeur attendue par votre logique)
    """
    response = await client.get("/health")
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] == True
    assert "version" in data