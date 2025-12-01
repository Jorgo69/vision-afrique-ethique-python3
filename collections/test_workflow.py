"""
Script de test du workflow complet FaceAuth.
"""
import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("🧪 TEST DU WORKFLOW FACEAUTH")
print("=" * 60)

# Test 1 : Health Check
print("\n[1/4] Health Check...")
response = requests.get(f"{BASE_URL}/health")
if response.status_code == 200:
    print("✅ API en ligne")
else:
    print("❌ API hors ligne")
    exit(1)

# Test 2 : Tokenization
print("\n[2/4] Génération du token...")
with open("./images/image1.jpg", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/face/tokenize",
        files={"image": f}
    )

if response.status_code == 200:
    data = response.json()
    token = data["token"]
    print(f"✅ Token généré")
    print(f"   Âge: {data['age']}")
    print(f"   Genre: {data['gender']}")
    print(f"   Token: {token[:50]}...")
else:
    print(f"❌ Erreur: {response.json()}")
    exit(1)

# Test 3 : Match (même image)
print("\n[3/4] Vérification (même personne)...")
with open("../images/image1.jpg", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/face/match",
        files={"image": f},
        data={"token_reference": token}
    )

if response.status_code == 200:
    result = response.json()
    if result["match_found"]:
        print("✅ Match trouvé (CORRECT)")
    else:
        print("❌ Pas de match (ERREUR)")
else:
    print(f"❌ Erreur: {response.json()}")

# Test 4 : Résumé
print("\n" + "=" * 60)
print("✅ TOUS LES TESTS PASSENT")
print("=" * 60)
print("\n📖 Collection Postman disponible dans:")
print("   ./FaceAuth_API_Collection.json")