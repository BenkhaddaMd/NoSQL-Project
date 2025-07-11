# SupDeVinci Travel Hub (STH)

SupDeVinci Travel Hub (STH) est une plateforme B2C qui agrège vols, hébergements et activités touristiques pour construire des itinéraires personnalisés quasi en temps réel. Ce projet met en œuvre une architecture polyglotte basée sur FastAPI, Redis, MongoDB, et Neo4j.

## Stack technique

| Composant | Rôle                                         | Base de données | Modèle          |
| --------- | -------------------------------------------- | --------------- | --------------- |
| FastAPI   | API HTTP/JSON centralisée                    | -               | -               |
| Redis     | Cache, sessions, notifications temps réel    | Clé–valeur      | TTL, Pub/Sub    |
| MongoDB   | Catalogue d’offres (vols, hôtels, activités) | Document        | JSON            |
| Neo4j     | Recommandations de destinations              | Graphe          | Noeuds + Arêtes |

## Installation et lancement

1. Cloner le projet :
```bash
git clone https://github.com/BenkhaddaMd/NoSQL-Project.git
cd NoSQL-Project
```

3. Lancer les services avec Docker Compose :
```bash
docker-compose up --build
```
FastAPI est exposé sur http://localhost:8000.

## Liste des APIs

| Méthode | Endpoint                                                                         | Description                                                          |
| ------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `GET`   | `/offers`                                                                        | Recherche d’offres entre deux villes, avec cache Redis               |
|         | Params : `from`, `to`, `limit` <br> Exemple : `/offers?from=PAR&to=TYO&limit=10` |                                                                      |
| `GET`   | `/offers/{id}`                                                                   | Détails d’une offre, avec recommandations via Neo4j                  |
|         | Paramètre : `id` (ID de l’offre)                                                 |                                                                      |
| `GET`   | `/reco`                                                                          | Recommandations de villes proches selon un code-ville                |
|         | Params : `city`, `k` <br> Exemple : `/reco?city=PAR&k=3`                         |                                                                      |
| `POST`  | `/login`                                                                         | Authentifie un utilisateur et crée une session dans Redis            |
|         | Body JSON : `{ "userId": "u42" }`                                                |                                                                      |

## Auteurs :
1. Mohamed Dhia BEN AHMED
2. Mohamed BEN KHADDA


