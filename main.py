# Stub script

import os
import json

from flask import Flask

import matching.query as query

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    with open("build/index.html", "r") as f:
        html = f.read()
    return html

@app.route('/api/query', methods=["POST"])
def query():
    index_id = os.environ.get("MATCHING_ENGINE_DEPLOYED_INDEX_ID", "")
    ip = os.environ.get("MATCHING_ENGINE_ENDPOINT_IP", "")

    with open("build/embeddings/{}.json".format(request.form["query"]), "r") as f:
        embedding = json.loads(f.read())

    cli = query.MatchingQueryClient(ip, index_id)

    result, latency = cli.query_embedding(embedding)

    return html

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)