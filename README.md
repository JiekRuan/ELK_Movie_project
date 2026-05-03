# Movies ELK Platform

Projet d'analyse de films basé sur un dataset TMDB — pipeline d'ingestion Logstash, indexation Elasticsearch, dashboard Kibana et moteur de recherche Python.

## Prérequis

- Docker >= 24 et Docker Compose >= 2.20
- 4 Go de RAM disponibles minimum
- Ports libres : 9200, 9300, 5601, 9600, 8888, 8000

## Structure du projet

```
ELK_Movie_project/
├── docker-compose.yml
├── Dockerfile.jupyter
├── Search.py                   ← moteur de recherche (Python)
├── DATA/
│   └── movies.csv              ← dataset à placer ici (non versionné)
├── logstash/
│   └── pipeline/
│       └── logstash.conf       ← pipeline ingestion + nettoyage
├── logs/                       ← logs Logstash
├── notebooks/
│   ├── 01_exploration.ipynb    ← analyse exploratoire
│   └── Launcher.ipynb
└── docs/
    ├── mapping_movies_clean.json ← mapping Elasticsearch
    ├── queries.md              ← 12 requêtes DSL commentées
    ├── runbook.md              ← guide de lancement détaillé
    ├── data_cleaning.md        ← règles de nettoyage
    ├── Dico.md                 ← dictionnaire de données
    ├── Poker_planning.md       ← planning poker
    └── kibana_export.ndjson    ← dashboard Kibana (à exporter depuis Kibana)
```

## Flux de données

```
movies.csv → Logstash → movies_raw (données brutes)
                     → movies_clean (nettoyé, typé, enrichi)
                              ↓
                        Kibana Dashboard
                        Moteur de recherche
```

## Démarrage rapide

### 1. Cloner le repo et placer le dataset

```bash
git clone https://github.com/JiekRuan/ELK_Movie_project.git
cd ELK_Movie_project

cp /chemin/vers/movies.csv DATA/movies.csv
```

### 2. Appliquer le mapping avant de lancer Logstash

Important : si on lance Logstash avant d'appliquer le mapping, Elasticsearch
va créer l'index tout seul avec des types incorrects.

```bash
docker compose up -d elasticsearch

# attendre ~30 secondes puis vérifier
docker compose ps

curl -X PUT http://localhost:9200/movies_clean \
  -H "Content-Type: application/json" \
  -d @docs/mapping_movies_clean.json
```

### 3. Lancer la stack complète

```bash
docker compose up -d

# vérifier que tout tourne
docker compose ps
```

### 4. Suivre l'ingestion

```bash
docker compose logs -f logstash

# compter les documents indexés
curl -s http://localhost:9200/movies_raw/_count
curl -s http://localhost:9200/movies_clean/_count
```

### 5. Accéder aux outils

| Outil | URL | Info |
|-------|-----|------|
| Kibana | http://localhost:5601 | exploration et dashboard |
| Jupyter | http://localhost:8888 | token : `movieslab` |
| Moteur de recherche | http://localhost:8000 | lancer Search.py avant |

Pour le moteur de recherche :

```bash
python Search.py
```

### 6. Importer le dashboard Kibana

Menu → Stack Management → Saved Objects → Import → sélectionner `docs/kibana_export.ndjson`

### 7. Arrêter la stack

```bash
docker compose down

# reset complet avec suppression des données
docker compose down -v
```

## Index Elasticsearch

| Index | Description |
|-------|-------------|
| `movies_raw` | Ingestion brute, pas de transformation |
| `movies_clean` | Données nettoyées, typées, avec champs calculés (profit, roi_pct, release_year) |

## Documentation

Tout est dans le dossier `docs/` :

- `runbook.md` — guide de démarrage complet avec dépannage
- `queries.md` — 12 requêtes DSL commentées
- `data_cleaning.md` — ce qu'on corrige entre raw et clean
- `Dico.md` — description de tous les champs
- `mapping_movies_clean.json` — mapping Elasticsearch
- `Poker_planning.md` — répartition des tâches

## Dépannage rapide

| Problème | Solution |
|----------|---------|
| ES ne démarre pas | Réduire `ES_JAVA_OPTS` à `-Xms512m -Xmx512m` dans docker-compose.yml |
| `movies_raw` count = 0 | Vérifier que `DATA/movies.csv` existe |
| `movies_clean` vide | Appliquer le mapping avant de relancer Logstash |
| Kibana timeout | Attendre qu'Elasticsearch soit healthy avant |
