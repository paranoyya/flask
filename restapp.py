import json
import postgresql
import flask
import urllib.parse

app = flask.Flask(__name__)

# Port on which JSON should be served up
PORT = 8001

# Database connection info
DB_NAME = 'rvision'
DB_HOST = 'localhost'
DB_USER = '10.252.40.4'

DB = postgresql.open(host=DB_HOST, database=DB_NAME, user=DB_USER)

@app.route("/search/<query>/")
@app.route("/search/<query>/<int:page>")
@app.route("/search/<query>/<int:page>/<int:limit>")
def search(query, page=0, limit=10):
    """Return JSON formatted search results, including snippets and facets"""

    query = urllib.parse.unquote(query)
    results = __get_ranked_results(query, limit, page)
    count = __get_result_count(query)

    resj = json.dumps({
        'query': query,
        'results': results,
        'meta': {
            'total': count,
            'page': page,
            'limit': limit,
            'results': len(results)
        }
    })
    return flask.Response(response=str(resj), mimetype='application/json')

def __get_ranked_results(query, limit, page):
    """Simple search for terms, with optional limit and paging"""

    sql = """
        WITH q AS (SELECT plainto_tsquery($1) AS query),
        ranked AS (
            SELECT id, doc, ts_rank(tsv, query) AS rank
            FROM fulltext_search, q
            WHERE q.query @@ tsv
            ORDER BY rank DESC
            LIMIT $2 OFFSET $3
        )
        SELECT id, ts_headline(doc, q.query, 'MaxWords=75,MinWords=25,ShortWord=3,MaxFragments=3,FragmentDelimiter="||||"')
        FROM ranked, q
        ORDER BY ranked DESC
    """

    cur = DB.prepare(sql)
    results = []
    for row in cur(query, limit, page*limit):
        results.append({
            'id': row[0],
            'snippets': row[1].split('||||')
        })

    return results

def __get_result_count(query):
    """Gather count of matching results"""

    sql = """
        SELECT COUNT(*) AS rescnt
        FROM fulltext_search 
        WHERE plainto_tsquery($1) @@ tsv
    """
    cur = DB.prepare(sql)
    count = cur.first(query)
    return count

if __name__ == "__main__":
    app.debug = True
    app.run(port=PORT)