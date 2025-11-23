# test_match.py
import requests

# ⚠️ REMPLACEZ ce token par celui que vous venez de recevoir
TOKEN = "$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJlX2NoYWluZQ$+Ag6nAszhHAb9GObNNHmtayySFARMFvOx7vaOOabulY"

url = "http://localhost:8000/face/match"

# Test avec la MÊME image
with open("./client/images/image1.jpg", "rb") as f:
    files = {"image": ("image1.jpg", f, "image/jpeg")}
    data = {"token_reference": TOKEN}
    response = requests.post(url, files=files, data=data)
    
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    print("\n✅ Match trouvé !" if response.json().get("match_found") else "\n❌ Pas de match")