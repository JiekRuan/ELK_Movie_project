# Requêtes DSL - Movies ELK Platform

12 requêtes commentées pour analyser le dataset TMDB depuis Elasticsearch.
Toutes ces requêtes tournent sur l'index `movies_clean`.

---

## Requête 1 - Top 10 des langues les plus représentées

On veut savoir quelles langues dominent le dataset. On utilise une agrégation
`terms` sur le champ `original_language` qui est en keyword, donc parfait pour
un GROUP BY. Le `size: 10` limite aux 10 premières.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "langues": {
      "terms": {
        "field": "original_language",
        "size": 10
      }
    }
  }
}
```

---

## Requête 2 - Top 10 des films les plus populaires

Ici on liste les films, pas d'agrégation. On trie par `popularity` décroissant
et on limite aux champs utiles avec `_source` pour ne pas ramener tout le document.

```json
GET movies_clean/_search
{
  "size": 10,
  "_source": ["title", "popularity", "vote_average", "release_year", "genres"],
  "query": {
    "match_all": {}
  },
  "sort": [
    { "popularity": { "order": "desc" } }
  ]
}
```

---

## Requête 3 - Films bien notés avec un volume de votes significatif

Un film avec 9.5 de moyenne sur 3 votes ça veut rien dire. On filtre donc
sur `vote_average >= 7.5` ET `vote_count >= 500` pour avoir des résultats fiables.
On utilise `filter` plutôt que `must` parce qu'on veut juste filtrer, pas scorer.

```json
GET movies_clean/_search
{
  "size": 20,
  "_source": ["title", "vote_average", "vote_count", "genres", "release_year"],
  "query": {
    "bool": {
      "filter": [
        { "range": { "vote_average": { "gte": 7.5 } } },
        { "range": { "vote_count": { "gte": 500 } } }
      ]
    }
  },
  "sort": [
    { "vote_average": { "order": "desc" } }
  ]
}
```

---

## Requête 4 - Evolution du volume de sorties de films par année

On groupe les films par année de sortie avec `date_histogram`. L'intervalle
`calendar_interval: year` crée automatiquement un bucket par année.
Le `min_doc_count: 1` évite d'afficher les années sans film.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "sorties_par_annee": {
      "date_histogram": {
        "field": "release_date",
        "calendar_interval": "year",
        "min_doc_count": 1
      }
    }
  }
}
```

---

## Requête 5 - Répartition des films par genre

Même principe que la requête 1 mais sur les genres. Comme `genres` est un
tableau de keywords, Elasticsearch va compter chaque genre séparément,
ce qui est exactement ce qu'on veut.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "genres": {
      "terms": {
        "field": "genres",
        "size": 20
      }
    }
  }
}
```

---

## Requête 6 - Recherche full-text avec tolérance aux fautes de frappe

On cherche dans le titre et l'overview en même temps. Le `title` est boosté x3
parce que si le mot apparaît dans le titre c'est plus pertinent que dans le synopsis.
`fuzziness: AUTO` tolère les petites fautes de frappe.

```json
GET movies_clean/_search
{
  "size": 10,
  "_source": ["title", "overview", "vote_average", "release_year"],
  "query": {
    "multi_match": {
      "query": "space adventure",
      "fields": ["title^3", "overview", "tagline", "keywords"],
      "fuzziness": "AUTO"
    }
  }
}
```

---

## Requête 7 - Note moyenne par langue (agrégation imbriquée)

On groupe d'abord par langue, puis dans chaque groupe on calcule la note moyenne.
C'est l'équivalent d'un `SELECT language, AVG(vote_average) GROUP BY language` en SQL.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "par_langue": {
      "terms": {
        "field": "original_language",
        "size": 15
      },
      "aggs": {
        "note_moyenne": {
          "avg": {
            "field": "vote_average"
          }
        }
      }
    }
  }
}
```

---

## Requête 8 - Distribution des notes (histogramme)

On veut voir comment les notes sont réparties entre 0 et 10. L'intervalle de 0.5
donne assez de granularité sans être trop fragmenté.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "distribution_notes": {
      "histogram": {
        "field": "vote_average",
        "interval": 0.5,
        "min_doc_count": 1
      }
    }
  }
}
```

---

## Requête 9 - Films avec les meilleurs retours financiers

On filtre sur `has_financials: true` pour ne garder que les films avec des données
complètes, puis on trie par `roi_pct` pour voir qui a le mieux rentabilisé son budget.

```json
GET movies_clean/_search
{
  "size": 10,
  "_source": ["title", "budget", "revenue", "profit", "roi_pct", "release_year"],
  "query": {
    "bool": {
      "filter": [
        { "term": { "has_financials": true } },
        { "range": { "budget": { "gte": 1000000 } } }
      ]
    }
  },
  "sort": [
    { "roi_pct": { "order": "desc" } }
  ]
}
```

---

## Requête 10 - Films sans overview (données manquantes)

Utile pour mesurer la qualité du dataset. On cherche les documents où le champ
`overview` n'existe pas, avec `must_not exists`.

```json
GET movies_clean/_search
{
  "size": 0,
  "query": {
    "bool": {
      "must_not": [
        { "exists": { "field": "overview" } }
      ]
    }
  },
  "aggs": {
    "sans_overview_par_langue": {
      "terms": {
        "field": "original_language",
        "size": 10
      }
    }
  }
}
```

---

## Requête 11 - Recherche combinée avec filtres métier

Requête type moteur de recherche : on cherche un terme dans le texte, on filtre
par langue et on exclut les films trop peu votés pour avoir une note fiable.
C'est ce genre de requête qui tourne derrière le moteur de recherche.

```json
GET movies_clean/_search
{
  "size": 10,
  "_source": ["title", "overview", "genres", "vote_average", "release_year"],
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "superhero",
            "fields": ["title^3", "overview", "keywords"],
            "fuzziness": "AUTO"
          }
        }
      ],
      "filter": [
        { "term": { "original_language": "en" } },
        { "range": { "vote_count": { "gte": 100 } } },
        { "range": { "release_year": { "gte": 2000 } } }
      ]
    }
  },
  "sort": ["_score", { "popularity": { "order": "desc" } }]
}
```

---

## Requête 12 - Classement qualité des films (quality_band)

On catégorise les films en 3 bandes selon leur note :
- A : note >= 7 (bons films)
- B : note entre 5 et 7 (films moyens)
- C : note < 5 (films mal notés)

On utilise une agrégation `range` sur `vote_average` et on filtre sur les films
avec assez de votes pour que la note soit représentative.

```json
GET movies_clean/_search
{
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        { "range": { "vote_count": { "gte": 50 } } }
      ]
    }
  },
  "aggs": {
    "quality_band": {
      "range": {
        "field": "vote_average",
        "ranges": [
          { "key": "C", "to": 5 },
          { "key": "B", "from": 5, "to": 7 },
          { "key": "A", "from": 7 }
        ]
      }
    }
  }
}
```
