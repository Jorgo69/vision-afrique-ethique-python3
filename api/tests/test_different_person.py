# test_different_person.py
import requests

# Token généré avec image1.jpg
TOKEN = "$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJlX2NoYWluZQ$+Ag6nAszhHAb9GObNNHmtayySFARMFvOx7vaOOabulY"

url = "http://localhost:8000/face/match"

# Si vous avez une autre image de personne différente
try:
    with open("./images/image2.jpg", "rb") as f:
        response = requests.post(
            url,
            files={"image": f},
            data={"token_reference": TOKEN}
        )
        result = response.json()
        print("Status Code:", response.status_code)
        print("Response:", result)
        
        if not result.get("match_found"):
            print("\n✅ Système fonctionne : Personnes différentes détectées correctement")
        else:
            print("\n⚠️ Attention : Match trouvé alors que les personnes sont différentes")
            
except FileNotFoundError:
    print("⚠️ image2.jpg n'existe pas. Créez-en une pour tester la non-correspondance.")