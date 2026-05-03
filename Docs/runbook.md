# Runbook - Movies ELK Platform

Guide de démarrage complet depuis zéro.

## Ce qu'il faut avoir installé

- Docker >= 24
- Docker Compose >= 2.20
- 4 Go de RAM disponibles minimum
- Ports libres : 9200, 9300, 5601, 9600, 8888

## 1. Récupérer le projet

```bash
git clone https://github.com/JiekRuan/ELK_Movie_project.git
cd ELK_Movie_project
```

## 2. Placer le dataset

Copier le fichier CSV dans le dossier DATA :

```bash
cp /chemin/vers/movies.csv DATA/movies.csv
```

Le fichier doit s'appeler exactement `movies.csv` et être dans `DATA/`.

## 3. Appliquer le mapping avant de lancer Logstash

On démarre Elasticsearch seul d'abord, on attend qu'il soit prêt, puis on crée l'index avec le bon mapping. Si on lance Logstash avant, il va créer l'index tout seul avec un mapping automatique et on perd le contrôle sur les types.

```bash
docker compose up -d elasticsearch

# attendre environ 30 secondes puis vérifier
docker compose ps

# appliquer le mapping movies_clean
curl -X PUT http://localhost:9200/movies_clean \
  -H "Content-Type: application/json" \
  -d @docs/mapping_movies_clean.json

# vérifier que l'index existe
curl http://localhost:9200/movies_clean/_mapping
```

## 4. Démarrer la stack complète

```bash
docker compose up -d
```

Vérifier que tout tourne :

```bash
docker compose ps
# elasticsearch -> healthy
# kibana        -> healthy
# logstash      -> running
# jupyter       -> healthy
```

## 5. Suivre l'ingestion Logstash

L'ingestion démarre automatiquement quand Logstash se lance. On peut suivre les logs en direct :

```bash
docker compose logs -f logstash
```

Vérifier le nombre de documents indexés :

```bash
curl -s http://localhost:9200/movies_raw/_count
curl -s http://localhost:9200/movies_clean/_count
```

Si le count reste à 0 après quelques minutes, voir la section dépannage en bas.

## 6. Accéder aux outils

- Kibana : http://localhost:5601
- Jupyter : http://localhost:8888 (token : movieslab)
- Moteur de recherche : http://localhost:8000

Pour le moteur de recherche, le lancer séparément :

```bash
python Search.py
```

## 7. Arrêter la stack

```bash
docker compose down

# reset complet avec suppression des données
docker compose down -v
```

## Dépannage

**Le count reste à 0 dans movies_raw ou movies_clean**

Vérifier que le CSV est bien dans DATA/ :
```bash
ls -lh DATA/
```

Vérifier les logs Logstash pour voir s'il y a une erreur :
```bash
docker compose logs logstash | tail -50
```

Forcer une réingestion complète en supprimant le sincedb :
```bash
docker compose restart logstash
```

**Elasticsearch ne démarre pas**

Manque de mémoire souvent. Réduire dans docker-compose.yml :
```
ES_JAVA_OPTS=-Xms512m -Xmx512m
```

**movies_clean vide alors que movies_raw a des documents**

Le mapping n'a pas été appliqué avant le démarrage de Logstash. Supprimer l'index et recommencer :
```bash
curl -X DELETE http://localhost:9200/movies_clean
curl -X PUT http://localhost:9200/movies_clean \
  -H "Content-Type: application/json" \
  -d @docs/mapping_movies_clean.json
docker compose restart logstash
```
