# Dictionnaire de données — movies_clean

Source : movies.csv (Kaggle — Millions of Movies, v67)
Lignes totales : ~769 631

---

## Champs

| Champ | Type ES | Type brut CSV | Description | Valeurs manquantes | Nettoyage appliqué |
|-------|---------|--------------|-------------|-------------------|-------------------|
| `id` | integer | int | Identifiant unique TMDB | 0 | Aucun |
| `title` | text + keyword | string | Titre du film | 0 | Aucun |
| `genres` | keyword[] | string | Genres séparés par "-" | ~1% | Split sur "-" → tableau |
| `original_language` | keyword | string | Code ISO 639-1 (en, fr…) | 0 | Aucun |
| `overview` | text | string | Synopsis | ~1% | Supprimé si vide |
| `popularity` | float | float | Score popularité TMDB | 0 | Aucun |
| `production_companies` | keyword[] | string | Sociétés séparées par "-" | ~7% | Split sur "-" → tableau |
| `release_date` | date | string YYYY-MM-DD | Date de sortie | ~0.2% | Parsé en date ISO |
| `release_year` | integer | — | Année extraite de release_date | calculé | Ruby filter |
| `budget` | long | float | Budget en USD | ~57% à 0 | 0 → null |
| `revenue` | long | float | Recettes en USD | ~53% à 0 | 0 → null |
| `runtime` | float | float | Durée en minutes | rare à 0 | 0 → null |
| `status` | keyword | string | Released, In Production… | 0 | Aucun |
| `tagline` | text | string | Accroche du film | ~34% | Supprimé si vide |
| `vote_average` | float | float | Note moyenne /10 | 0 | Aucun |
| `vote_count` | integer | float | Nombre de votes | 0 | Cast en integer |
| `credits` | keyword[] | string | Acteurs séparés par "-" | ~1% | Split sur "-" → tableau |
| `keywords` | keyword[] | string | Mots-clés séparés par "-" | ~22% | Split sur "-" → tableau |
| `poster_path` | keyword | string | Chemin image poster TMDB | rare | Non indexé |
| `backdrop_path` | keyword | string | Chemin image backdrop TMDB | ~3% | Non indexé, supprimé si vide |
| `recommendations` | keyword[] | string | IDs films similaires sep. "-" | ~8% | Split sur "-" → tableau |
| `profit` | long | — | revenue - budget | calculé | Ruby filter (si has_financials) |
| `roi_pct` | float | — | (revenue-budget)/budget × 100 | calculé | Ruby filter (si has_financials) |
| `has_financials` | boolean | — | True si budget ET revenue > 0 | calculé | Ruby filter |

---

## Anomalies détectées

1. **Budget/revenue à 0** : ~57% des films n'ont pas de données financières → traités comme null
2. **Genres/keywords/credits en string** : séparateur "-" pouvant créer des ambiguïtés si un nom contient un tiret (ex: "Anya Taylor-Joy" → split incorrect)
3. **release_date manquante** : ~0.2% des films sans date
4. **tagline vide** : 34% des films sans accroche
5. **keywords manquants** : 22% des films sans mots-clés

---

## Mesure d'impact (avant/après nettoyage)

| Métrique | movies_raw | movies_clean |
|----------|-----------|-------------|
| Champs listés comme string | genres, keywords, credits, companies | tableaux natifs |
| Budget null vs 0 | 0 comme valeur | null (correctement absent) |
| has_financials | absent | calculé |
| profit / roi_pct | absent | calculés |
| release_year | absent | extrait de release_date |