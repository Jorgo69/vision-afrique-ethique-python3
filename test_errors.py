"""
Script de test des codes d'erreur.
Teste tous les cas d'erreur possibles.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_error(response):
    """Affiche proprement une erreur."""
    data = response.json()
    
    # FastAPI retourne soit "detail" directement, soit un objet structuré
    if "detail" in data:
        detail = data["detail"]
        
        # Si detail est un dict (notre format), l'afficher
        if isinstance(detail, dict) and "error" in detail:
            error = detail["error"]
            print(f"✅ Code: {error['code']}")
            print(f"   Message: {error['message']}")
            if "details" in error:
                print(f"   Détails: {error['details']}")
        else:
            # Sinon, afficher tel quel
            print(f"⚠️  Detail: {detail}")
    else:
        print(f"❌ Réponse inattendue: {json.dumps(data, indent=2)}")


print("=" * 60)
print("TEST DES CODES D'ERREUR")
print("=" * 60)

# Test 1 : Image trop grande
print("\n[1] Test : Image trop grande (11 MB)...")
large_data = b"x" * (11 * 1024 * 1024)  # 11 MB
try:
    response = requests.post(
        f"{BASE_URL}/face/extract",
        files={"image": ("large.jpg", large_data, "image/jpeg")}
    )
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print_error(response)
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2 : Format invalide
print("\n[2] Test : Format invalide (text/plain)...")
try:
    response = requests.post(
        f"{BASE_URL}/face/extract",
        files={"image": ("test.txt", b"not an image", "text/plain")}
    )
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print_error(response)
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3 : Image corrompue
print("\n[3] Test : Image corrompue...")
try:
    response = requests.post(
        f"{BASE_URL}/face/extract",
        files={"image": ("test.jpg", b"fake image data", "image/jpeg")}
    )
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print_error(response)
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 4 : Fichier vide
print("\n[4] Test : Fichier vide...")
try:
    response = requests.post(
        f"{BASE_URL}/face/extract",
        files={"image": ("test.jpg", b"", "image/jpeg")}
    )
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print_error(response)
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 5 : Succès avec une vraie image
print("\n[5] Test : Image valide (doit réussir)...")
try:
    with open("./images/image1.jpg", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/face/extract",
            # files={"image": f}
            files={"image": ("image1.jpg", f, "image/jpeg")}  # ✅ Spécifier le MIME type
        )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Succès !")
        print(f"   Âge: {data['age']}")
        print(f"   Genre: {data['gender']}")
        print(f"✅ Succès !")
        print(f"   Âge: {data['age']}")
        print(f"   Genre: {data['gender']}")
        print(f"   Embedding: {len(data['embedding'])} dimensions")
    else:
        print_error(response)
except FileNotFoundError:
    print("⚠️  Fichier ./images/image1.jpg introuvable")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 6 : Token invalide pour /match
print("\n[6] Test : Token invalide pour /match...")
try:
    with open("./images/image1.jpg", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/face/match",
            files={"image": f},
            data={"token_reference": "invalid_token"}
        )
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print_error(response)
except FileNotFoundError:
    print("⚠️  Fichier ./images/image1.jpg introuvable")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DES TESTS")
print("=" * 60)