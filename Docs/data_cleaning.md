# Règles de nettoyage - movies_clean

Résumé de ce qu'on fait sur les données entre movies_raw et movies_clean.

## Pourquoi deux index ?

movies_raw garde les données brutes telles qu'elles sortent du CSV, sans transformation. C'est utile pour comparer avant/après et pour debugger si quelque chose se passe mal dans le pipeline.

movies_clean est la version exploitable : types corrects, valeurs nulles gérées, champs calculés ajoutés.

## Ce qu'on corrige

### Types numériques

Dans le CSV tout arrive en texte. On convertit manuellement :

| Champ | Type CSV | Type final |
|-------|----------|------------|
| id | texte | integer |
| popularity | texte | float |
| budget | texte | long |
| revenue | texte | long |
| runtime | texte | float |
| vote_average | texte | float |
| vote_count | texte | integer |

Budget et revenue sont en `long` parce que les valeurs peuvent dépasser la limite d'un integer (films avec budget de plusieurs centaines de millions).

### Dates

La date de sortie arrive sous forme de texte `yyyy-MM-dd`. On la parse en champ date exploitable et on extrait l'année dans un champ `release_year` séparé pour faciliter les agrégations par année.

Les films avec une date invalide ou absente reçoivent le tag `_date_parse_failure` au lieu d'être supprimés - on préfère les garder et savoir combien ont ce problème.

### Champs liste

Les genres, keywords, crédits, sociétés de production et recommandations arrivent comme une seule chaîne avec des tirets comme séparateur (ex: `Action-Comedy-Drama`). On les split en tableaux pour pouvoir filtrer et agréger dessus correctement.

Limite connue : si un nom contient un tiret (ex: `Anya Taylor-Joy`), le split va le couper en deux. On l'accepte pour l'instant.

### Valeurs nulles

Budget et revenue à 0 veulent dire "donnée inconnue" dans ce dataset, pas vraiment 0 euros. On les remplace par null. Même chose pour runtime.

Les champs texte vides (tagline, overview, backdrop_path) sont supprimés plutôt que gardés comme string vide.

### Champs calculés

Trois champs sont calculés dans le pipeline :

- `profit` : revenue - budget (seulement si les deux sont renseignés)
- `roi_pct` : (revenue - budget) / budget * 100, arrondi à 2 décimales
- `has_financials` : booléen, true si budget ET revenue > 0

Ces champs n'existent que pour les films qui ont des données financières complètes.

## Mesure d'impact

| Métrique | movies_raw | movies_clean |
|----------|-----------|-------------|
| genres, keywords, credits | string avec tirets | tableaux |
| budget/revenue à 0 | valeur 0 | null |
| has_financials | absent | calculé |
| profit / roi_pct | absent | calculés si possible |
| release_year | absent | extrait de la date |

## Anomalies connues du dataset

- Environ 57% des films n'ont pas de budget renseigné
- 34% n'ont pas de tagline
- 22% n'ont pas de keywords
- 0.2% n'ont pas de date de sortie
- Le split sur "-" peut couper certains noms propres contenant un tiret
