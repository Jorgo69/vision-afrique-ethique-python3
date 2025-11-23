# test_api.py
import requests

url = "http://localhost:8000/face/tokenize"

with open("./client/images/image1.jpg", "rb") as f:
    files = {"image": ("image1.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)
    print(response.json())