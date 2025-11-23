Documentation : Phase 2 (Job Tokenize)
1. 🎯 Objectif de la Phase 2
L'objectif principal était de garantir que les données biométriques brutes (embedding 512 caractéristiques) ne sortent jamais du système sans avoir été transformées en un token cryptographique irréversible.

Endpoint créé : POST /face/tokenize

Résultat : Un token Argon2 hautement résistant à la force brute, remplaçant l'embedding brut dans la réponse.

2. 🛡️ Mécanisme de Double Hachage
Pour la sécurité, nous avons mis en place un processus en deux étapes dans security.py :

Hachage Préliminaire (SHA-256) :

Le vecteur d'embedding (512 floats) est sérialisé en bytes (via NumPy).

Un hachage SHA-256 est appliqué. Ceci convertit l'information biométrique complexe en une chaîne de 64 caractères unique et déterministe.

Hachage de Renforcement (Argon2) :

La chaîne SHA-256 est concaténée avec le secret VISION_SECRET_PART1 (servant de "mot de passe").

Le hachage Argon2 est appliqué. Argon2 est un algorithme coûteux en temps et en mémoire (défini par les paramètres t=2, m=65536, p=4), ce qui rend la recherche du vecteur d'origine extrêmement difficile, même pour des attaquants puissants. Le secret VISION_SECRET_PART2 est utilisé comme sel statique pour l'opération.

Le token résultant ($argon2id$...) inclut toutes les configurations de sécurité et les sels nécessaires à sa propre vérification, ce qui est essentiel pour la Phase 3.