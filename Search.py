"""
search_api.py — Mini moteur de recherche Movies
Connecté à Elasticsearch (index movies_clean)
Lancement : python search_api.py
Accès     : http://localhost:8000
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import urllib.request
import urllib.error

ES_HOST  = "http://localhost:9200"
ES_INDEX = "movies_clean"


def es_search(query: str, genre: str = None, language: str = None,
              year_from: int = None, year_to: int = None,
              min_rating: float = None, size: int = 10) -> dict:
    """Construit et exécute une requête bool vers Elasticsearch."""

    must_clauses   = []
    filter_clauses = []

    # ── Recherche full-text ──────────────────────────────────
    if query:
        must_clauses.append({
            "multi_match": {
                "query":     query,
                "fields":    ["title^3", "overview", "tagline", "keywords"],
                "type":      "best_fields",
                "fuzziness": "AUTO"
            }
        })
    else:
        must_clauses.append({"match_all": {}})

    # ── Filtres exacts ───────────────────────────────────────
    if genre:
        filter_clauses.append({"term": {"genres": genre}})

    if language:
        filter_clauses.append({"term": {"original_language": language}})

    if year_from or year_to:
        year_range = {}
        if year_from: year_range["gte"] = year_from
        if year_to:   year_range["lte"] = year_to
        filter_clauses.append({"range": {"release_year": year_range}})

    if min_rating:
        filter_clauses.append({"range": {"vote_average": {"gte": min_rating}}})

    es_query = {
        "size": size,
        "_source": [
            "id", "title", "overview", "genres", "original_language",
            "release_year", "vote_average", "vote_count",
            "popularity", "poster_path"
        ],
        "query": {
            "bool": {
                "must":   must_clauses,
                "filter": filter_clauses
            }
        },
        "sort": [
            "_score",
            {"popularity": {"order": "desc"}}
        ],
        "highlight": {
            "fields": {
                "title":    {},
                "overview": {"fragment_size": 200, "number_of_fragments": 1}
            }
        }
    }

    url  = f"{ES_HOST}/{ES_INDEX}/_search"
    body = json.dumps(es_query).encode("utf-8")
    req  = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        return {"error": str(e)}


def format_results(raw: dict) -> dict:
    """Formate la réponse ES pour l'API."""
    if "error" in raw:
        return raw

    hits  = raw.get("hits", {})
    total = hits.get("total", {}).get("value", 0)

    results = []
    for h in hits.get("hits", []):
        src  = h.get("_source", {})
        hl   = h.get("highlight", {})
        item = {
            "id":          src.get("id"),
            "title":       hl.get("title", [src.get("title", "")])[0],
            "overview":    hl.get("overview", [src.get("overview", "")])[0],
            "genres":      src.get("genres", []),
            "language":    src.get("original_language"),
            "year":        src.get("release_year"),
            "vote":        src.get("vote_average"),
            "vote_count":  src.get("vote_count"),
            "popularity":  src.get("popularity"),
            "poster":      f"https://image.tmdb.org/t/p/w200{src.get('poster_path', '')}",
            "score":       round(h.get("_score", 0), 3)
        }
        results.append(item)

    return {"total": total, "results": results}


# ─────────────────────────────────────────────────────────────
# Interface HTML
# ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Movies Search</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
    header { background: #1e293b; padding: 24px 32px; border-bottom: 1px solid #334155; }
    header h1 { font-size: 24px; color: #f8fafc; }
    header p  { color: #94a3b8; font-size: 14px; margin-top: 4px; }
    .search-box { padding: 24px 32px; background: #1e293b; }
    .filters { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; }
    .filter-group { display: flex; flex-direction: column; gap: 4px; }
    label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }
    input, select {
      background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
      padding: 8px 12px; border-radius: 6px; font-size: 14px; outline: none;
    }
    input:focus, select:focus { border-color: #6366f1; }
    #q { width: 280px; }
    button {
      background: #6366f1; color: #fff; border: none; padding: 9px 20px;
      border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;
    }
    button:hover { background: #4f46e5; }
    .results { padding: 24px 32px; }
    .meta { color: #64748b; font-size: 13px; margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
    .card {
      background: #1e293b; border: 1px solid #334155; border-radius: 10px;
      padding: 16px; display: flex; gap: 12px; transition: border-color .15s;
    }
    .card:hover { border-color: #6366f1; }
    .poster { width: 60px; height: 90px; object-fit: cover; border-radius: 6px; flex-shrink: 0; background: #334155; }
    .info { flex: 1; min-width: 0; }
    .card-title { font-weight: 600; font-size: 15px; color: #f1f5f9; margin-bottom: 4px; }
    .card-title em { background: #312e81; color: #a5b4fc; font-style: normal; padding: 0 2px; border-radius: 2px; }
    .card-meta { font-size: 12px; color: #64748b; margin-bottom: 6px; }
    .card-overview { font-size: 13px; color: #94a3b8; line-height: 1.5; }
    .card-overview em { background: #1e3a5f; color: #93c5fd; font-style: normal; padding: 0 2px; border-radius: 2px; }
    .badge {
      display: inline-block; padding: 2px 8px; border-radius: 4px;
      font-size: 11px; font-weight: 500; background: #1e3a5f; color: #93c5fd; margin: 2px;
    }
    .score { font-size: 11px; color: #475569; float: right; }
  </style>
</head>
<body>
  <header>
    <h1>🎬 Movies Search</h1>
    <p>Moteur de recherche connecté à Elasticsearch — index <code>movies_clean</code></p>
  </header>
  <div class="search-box">
    <div class="filters">
      <div class="filter-group">
        <label>Recherche</label>
        <input id="q" type="text" placeholder="Ex: space adventure, love Paris..." />
      </div>
      <div class="filter-group">
        <label>Genre</label>
        <select id="genre">
          <option value="">Tous</option>
          <option>Action</option><option>Adventure</option><option>Animation</option>
          <option>Comedy</option><option>Crime</option><option>Documentary</option>
          <option>Drama</option><option>Fantasy</option><option>Horror</option>
          <option>Mystery</option><option>Romance</option><option>Science Fiction</option>
          <option>Thriller</option><option>War</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Langue</label>
        <select id="lang">
          <option value="">Toutes</option>
          <option value="en">Anglais</option>
          <option value="fr">Français</option>
          <option value="es">Espagnol</option>
          <option value="ja">Japonais</option>
          <option value="ko">Coréen</option>
          <option value="it">Italien</option>
          <option value="de">Allemand</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Année (de)</label>
        <input id="year_from" type="number" placeholder="2000" style="width:90px" min="1900" max="2030" />
      </div>
      <div class="filter-group">
        <label>Année (à)</label>
        <input id="year_to" type="number" placeholder="2024" style="width:90px" min="1900" max="2030" />
      </div>
      <div class="filter-group">
        <label>Note min</label>
        <select id="rating">
          <option value="">Toutes</option>
          <option value="5">≥ 5.0</option>
          <option value="6">≥ 6.0</option>
          <option value="7">≥ 7.0</option>
          <option value="8">≥ 8.0</option>
        </select>
      </div>
      <button onclick="search()">Rechercher</button>
    </div>
  </div>
  <div class="results">
    <div class="meta" id="meta"></div>
    <div class="grid" id="grid"></div>
  </div>

  <script>
    async function search() {
      const q         = document.getElementById('q').value;
      const genre     = document.getElementById('genre').value;
      const lang      = document.getElementById('lang').value;
      const year_from = document.getElementById('year_from').value;
      const year_to   = document.getElementById('year_to').value;
      const rating    = document.getElementById('rating').value;

      const params = new URLSearchParams();
      if (q)         params.append('q',         q);
      if (genre)     params.append('genre',     genre);
      if (lang)      params.append('language',  lang);
      if (year_from) params.append('year_from', year_from);
      if (year_to)   params.append('year_to',   year_to);
      if (rating)    params.append('min_rating',rating);

      const resp = await fetch('/api/search?' + params.toString());
      const data = await resp.json();

      document.getElementById('meta').textContent =
        `${data.total ?? 0} résultat(s) trouvé(s)`;

      const grid = document.getElementById('grid');
      grid.innerHTML = '';

      (data.results || []).forEach(m => {
        const genres = (m.genres || []).map(g =>
          `<span class="badge">${g}</span>`).join('');
        grid.innerHTML += `
          <div class="card">
            <img class="poster" src="${m.poster}" onerror="this.style.display='none'" />
            <div class="info">
              <div class="score">score ${m.score}</div>
              <div class="card-title">${m.title}</div>
              <div class="card-meta">
                ${m.year ?? '?'} · ${m.language ?? '?'} · ⭐ ${m.vote ?? '?'} (${m.vote_count ?? 0})
              </div>
              <div>${genres}</div>
              <div class="card-overview">${m.overview || ''}</div>
            </div>
          </div>`;
      });
    }

    // Recherche au chargement
    document.getElementById('q').addEventListener('keydown', e => {
      if (e.key === 'Enter') search();
    });
    search();
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────
# Serveur HTTP
# ─────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")

    def do_GET(self):
        parsed = urlparse(self.path)

        # ── UI HTML ─────────────────────────────────────────
        if parsed.path == "/" or parsed.path == "":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))

        # ── API JSON ─────────────────────────────────────────
        elif parsed.path == "/api/search":
            qs = parse_qs(parsed.query)
            get = lambda k, d=None: qs[k][0] if k in qs else d

            raw = es_search(
                query     = get("q", ""),
                genre     = get("genre"),
                language  = get("language"),
                year_from = int(get("year_from")) if get("year_from") else None,
                year_to   = int(get("year_to"))   if get("year_to")   else None,
                min_rating= float(get("min_rating")) if get("min_rating") else None,
                size      = int(get("size", "20"))
            )
            result = format_results(raw)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = 8000
    print(f"🎬 Movies Search démarré → http://localhost:{port}")
    print(f"   ES  : {ES_HOST}/{ES_INDEX}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()