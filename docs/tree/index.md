#### Arborescence Adapoter

estructuration de l'Architecture (Méthode Modulaire FastAPI)

Pour adopter une structure inspirée des frameworks MVC/Modulaires, nous allons utiliser les concepts clés de FastAPI : APIRouter et la gestion des dépendances/services.

    vision-afrique-ethique/
```
├── api/
│   └── endpoints/
│       └── face.py         # ⬅️ Nouveau : Le "Controller" (Routes et logique de réception HTTP)
├── core/
│   ├── config.py           # ⬅️ Nouveau : Gestion propre de la configuration/secrets
│   └── models.py           # ⬅️ Nouveau : Schémas de données (Pydantic)
├── services/
│   └── face_extractor.py   # ⬅️ Nouveau : Le "Service" (Logique métier et appel InsightFace)
├── app.py                  # ⬅️ Le point d'entrée minimal (similaire à "main.ts" ou "server.php")
├── security.py             # (Prévu pour la Phase 2)
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

{
  "status": "success",
  "age": 24,
  "gender": "M",
  "token": "$argon2id$v=19$m=65536,t=2,p=4$dW5lX2F1dHJlX2NoYWluZV9kaWZmZXJlbnRfZXRfZWdhbGVtZW50X3RyZXNfbG9uZ3VlX21pbmltdW1fMzJfZXRfcGx1cw$C/1Q+2YtvhYkFVTDlLR8aGxVxwAe7toQh4SdWSnnkB8"
}