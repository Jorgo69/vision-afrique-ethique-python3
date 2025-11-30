"""Configuration commune pour les tests."""
import pytest
from httpx import AsyncClient, ASGITransport
from app import app
from services.face_extractor import load_insightface_model  # ✅ AJOUTÉ

# ============================================
# SETUP : Charger le modèle avant les tests
# ============================================

@pytest.fixture(scope="session", autouse=True)
def setup_model():
    """
    Charge le modèle InsightFace une fois avant tous les tests.
    autouse=True : s'exécute automatiquement.
    """
    print("\n🔧 Setup : Chargement du modèle InsightFace pour les tests...")
    load_insightface_model()
    print("✅ Modèle chargé avec succès !\n")
    yield  # Les tests s'exécutent ici
    print("\n🧹 Teardown : Nettoyage après les tests...")


# ============================================
# FIXTURE : Client de Test Asynchrone
# ============================================

@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    """
    Client de test asynchrone pour l'application FastAPI.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac


# ============================================
# FIXTURE : Images de Test
# ============================================

@pytest.fixture
def sample_image_path():
    """Chemin vers une image de test valide."""
    return "tests/fixtures/test_face.jpg"


@pytest.fixture
def sample_image_bytes(sample_image_path):
    """Lit les bytes d'une image de test."""
    with open(sample_image_path, "rb") as f:
        return f.read()


@pytest.fixture
def invalid_image_bytes():
    """Bytes invalides (pas une image)."""
    return b"Ceci n'est pas une image valide"


@pytest.fixture
def empty_image_bytes():
    """Bytes vides."""
    return b""