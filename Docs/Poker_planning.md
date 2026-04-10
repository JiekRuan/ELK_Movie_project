# Planning Poker — Movies Data Platform

## Échelle utilisée : Fibonacci (1, 2, 3, 5, 8, 13)

| Points | Signification |
|--------|---------------|
| 1      | Trivial, moins d'une heure |
| 2      | Simple, quelques heures |
| 3      | Modéré, demi-journée |
| 5      | Complexe, une journée |
| 8      | Très complexe, 2 jours |
| 13     | Epic, à découper |

---

## Backlog & Estimations

| ID  | Feature | Membre | Est. initiale | Est. finale | Hypothèses |
|-----|---------|--------|--------------|-------------|------------|
| F1  | Bootstrap stack Docker | Membre A | 3 | 3 | Config single-node, pas de TLS |
| F2  | Ingestion brute movies_raw | Membre B | 5 | 5 | CSV ~770k lignes, champs connus |
| F3  | Nettoyage & normalisation Logstash | Membre B | 8 | 8 | Parsing listes "-", dates, nulls |
| F4  | Mapping movies_clean + analyzer | Membre A | 5 | 5 | Analyzer custom anglais + stemmer |
| F5  | 12 requêtes DSL commentées | Membre C | 5 | 5 | 5 bool min, cas métier réels |
| F6  | Dashboard Kibana 6-8 visu | Membre D | 5 | 5 | Export .ndjson requis |
| F7  | Documentation complète | Tous    | 5 | 5 | runbook, dictionnaire, nettoyage |
| F8  | Moteur de recherche | Membre C | 5 | 3 | Python stdlib, pas de framework |

---

## Répartition des features par membre

| Membre | Features | Rôle |
|--------|----------|------|
| Membre A (Lead tech) | F1, F4 | Docker, mapping ES |
| Membre B | F2, F3 | Pipeline Logstash, nettoyage données |
| Membre C | F5, F8 | Requêtes DSL, moteur de recherche |
| Membre D | F6, F7 | Kibana dashboard, documentation |

---

## Notes de session

- Date du planning poker : à renseigner
- Outil utilisé : cartes physiques / planningpoker.com
- Hypothèse principale : le dataset movies.csv est stable (pas de mise à jour pendant le projet)
- Risque identifié : volume élevé (~770k lignes) peut ralentir l'ingestion Logstash → prévoir un échantillon de test