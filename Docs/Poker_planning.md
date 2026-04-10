# Planning Poker — Movies Data Platform

## Équipe : 2 

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

| ID  | Feature | Membre responsable | Est. Membre 1 | Est. Membre 2 | Est. finale retenue | Hypothèses |
|-----|---------|-------------------|--------------|--------------|---------------------|------------|
| F1  | Bootstrap stack Docker | Membre 1 | 3 | 2 | 3 | Config single-node, pas de TLS |
| F2  | Ingestion brute movies_raw | Membre 1 | 5 | 5 | 5 | CSV ~770k lignes, champs connus |
| F3  | Nettoyage & normalisation Logstash | Membre 1 | 8 | 8 | 8 | Parsing listes "-", dates, nulls |
| F4  | Mapping movies_clean + analyzer | Membre 2 | 5 | 3 | 5 | Analyzer custom anglais + stemmer |
| F5  | 12 requêtes DSL commentées | Membre 2 | 5 | 5 | 5 | 5 bool min, cas métier réels |
| F6  | Dashboard Kibana 6-8 visu | Membre 2 | 5 | 8 | 5 | Export .ndjson requis |
| F7  | Documentation complète | Membres 1 & 2 | 5 | 5 | 5 | runbook, dictionnaire, nettoyage |
| F8  | Moteur de recherche | Membre 2 | 3 | 3 | 3 | Python stdlib, pas de framework |

---

## Répartition des features par membre

| Membre | Features | Rôle |
|--------|----------|------|
| Jiek (Lead tech) | F1, F2, F3 | Docker, ingestion Logstash, nettoyage données |
| Omar | F4, F5, F6, F8 | Mapping ES, requêtes DSL, Kibana, moteur de recherche |
| Les deux | F7 | Documentation finale |

---

## Règles Gitflow rappelées

- Chaque membre ouvre **au moins 1 PR** et **review au moins 1 PR** de l'autre
- Aucun push direct sur `main` ou `dev`
- Branches : `feature/<id>-<slug>` (ex: `feature/F1-docker-bootstrap`)

---

## Notes de session

- Date du planning poker : à renseigner
- Outil utilisé : cartes physiques / planningpoker.com
- Hypothèse principale : le dataset movies.csv est stable (pas de mise à jour pendant le projet)
- Risque identifié : volume élevé (~770k lignes) peut ralentir l'ingestion Logstash → prévoir un échantillon de test sur les 10 000 premières lignes
- Risque identifié : équipe de 2 → charge plus élevée par personne, prioriser F1→F2→F3 en premier