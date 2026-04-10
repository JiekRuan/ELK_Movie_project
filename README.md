# Movies Data Platform

## Prérequis

- Docker ≥ 24 et Docker Compose ≥ 2.20
- RAM disponible : 4 Go minimum (ES + Kibana + Logstash)
- Port libres : 9200, 9300, 5601, 9600

---

## 1. Cloner le repo et placer le CSV

```bash
git clone https://github.com/JiekRuan/movies-elk.git

# Copier le dataset dans le dossier DATA/
cp /chemin/vers/movies.csv DATA/movies.csv
```

---

## 2. Créer le mapping avant l'ingestion

```bash
# Démarrer uniquement Elasticsearch en premier
docker compose up -d elasticsearch

# Attendre qu'il soit healthy (~30s)
docker compose ps

# Appliquer le mapping movies_clean
curl -X PUT http://localhost:9200/movies_clean \
  -H "Content-Type: application/json" \
  -d @docs/mapping_movies_clean.json

# Vérifier
curl http://localhost:9200/movies_clean/_mapping | python3 -m json.tool | head -30
```

---

## 3. Démarrer la stack complète

```bash
docker compose up -d
```

Vérifier l'état des services :

```bash
docker compose ps
# elasticsearch → healthy
# kibana        → healthy
# logstash      → running (démarre l'ingestion automatiquement)
```

---

## 4. Suivre l'ingestion Logstash

```bash
# Logs en temps réel
docker compose logs -f logstash

# Vérifier le compte de documents (toutes les 30s pendant l'ingestion)
watch -n 30 'curl -s http://localhost:9200/movies_raw/_count | python3 -m json.tool'
```

---

## 5. Vérifier l'ingestion

```bash
# Nombre de docs dans movies_raw
curl -s http://localhost:9200/movies_raw/_count

# Nombre de docs dans movies_clean
curl -s http://localhost:9200/movies_clean/_count

# Échantillon movies_raw
curl -s "http://localhost:9200/movies_raw/_search?size=1&pretty"

# Échantillon movies_clean
curl -s "http://localhost:9200/movies_clean/_search?size=1&pretty"
```

---

## 6. Ouvrir Kibana

Ouvrir http://localhost:5601 dans un navigateur.

Pour importer le dashboard :
- Menu → Stack Management → Saved Objects → Import
- Sélectionner `docs/kibana_export.ndjson`

---

## 7. Lancer le moteur de recherche

```bash
cd search-api
python3 search_api.py
# Ouvrir http://localhost:8000
```

---

## 8. Arrêter la stack

```bash
docker compose down

# Supprimer aussi les volumes (reset complet)
docker compose down -v
```

---

## Résolution de problèmes courants

| Problème | Cause probable | Solution |
|----------|---------------|---------|
| ES ne démarre pas | Mémoire insuffisante | Réduire ES_JAVA_OPTS à -Xms256m -Xmx256m |
| Logstash crash loop | movies.csv absent | Vérifier DATA/movies.csv |
| movies_clean vide | Mapping absent avant ingestion | Relancer après avoir appliqué le mapping |
| Kibana timeout | ES pas encore prêt | Attendre healthcheck ES (service_healthy) |

# Movies Data Platform — ELK Stack

Projet d'analyse de films avec la stack Elasticsearch / Logstash / Kibana.

## Structure du projet

```
movies-elk/
├── docker-compose.yml
├── DATA/
│   └── movies.csv              ← dataset Kaggle (à placer ici)
├── logstash/
│   └── pipeline/
│       └── logstash.conf       ← pipeline ingestion + nettoyage
├── logs/                       ← logs Logstash (créé automatiquement)
├── search-api/
│   └── search_api.py           ← moteur de recherche (Python stdlib)
└── docs/
    ├── mapping_movies_clean.json
    ├── queries.md
    ├── planning_poker.md
    ├── data_dictionary.md
    ├── data_cleaning.md
    ├── runbook.md
    ├── project_management.md
    ├── kibana_export.ndjson    ← à exporter depuis Kibana
    ├── demo_script.md
    └── demo.gif
```

## Démarrage rapide

```bash
# 1. Placer le dataset
cp movies.csv DATA/

# 2. Appliquer le mapping
docker compose up -d elasticsearch
curl -X PUT http://localhost:9200/movies_clean \
  -H "Content-Type: application/json" \
  -d @docs/mapping_movies_clean.json

# 3. Lancer la stack
docker compose up -d

# 4. Vérifier l'ingestion
curl http://localhost:9200/movies_clean/_count

# 5. Ouvrir Kibana
open http://localhost:5601

# 6. Lancer le moteur de recherche
python3 search-api/search_api.py
open http://localhost:8000
```

## Flux de données

```
movies.csv → Logstash → movies_raw (brut)
                     → movies_clean (nettoyé, typé, enrichi)
                             ↓
                         Kibana Dashboard
                         Moteur de recherche
```

## Index

| Index | Description |
|-------|-------------|
| `movies_raw` | Ingestion brute, aucune transformation |
| `movies_clean` | Données nettoyées, mappées, avec champs calculés |

## Documentation

Voir le dossier `docs/` :
- `runbook.md` — guide de lancement complet
- `data_dictionary.md` — description de tous les champs
- `data_cleaning.md` — règles de nettoyage et mesures d'impact
- `queries.md` — 12 requêtes DSL commentées
- `planning_poker.md` — estimation et répartition des features