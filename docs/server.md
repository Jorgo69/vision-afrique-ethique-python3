# Lancement du serveur Uvicorn
# app:app -> pointe vers l'instance 'app' dans le fichier 'app.py'
# --reload -> redémarre le serveur à chaque modification de code (pratique en dev)
# --host 0.0.0.0 --port 8000 -> rend l'API accessible sur toutes les interfaces (localhost:8000)
uvicorn app:app --reload --host 0.0.0.0 --port 8000