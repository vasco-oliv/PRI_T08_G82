#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

def fetch_solr_results(query_params, solr_uri, collection):
    """
    Fetch search results from a Solr instance based on the query parameters.

    Arguments:
    - query_params: Dictionary containing Solr query parameters.
    - solr_uri: URI of the Solr instance (e.g., http://localhost:8983/solr).
    - collection: Solr collection name from which results will be fetched.

    Output:
    - Returns the JSON search results.
    """
    # Construct the Solr request URL
    uri = f"{solr_uri}/{collection}/select?rows=50"

    try:
        # Send the POST request to Solr
        response = requests.post(uri, json=query_params)
        response.raise_for_status()  # Raise error if the request failed
    except requests.RequestException as e:
        return {"error": str(e)}

    # Fetch and return the results as JSON
    return response.json()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    subreddits = request.args.get('subreddits')
    dates = request.args.get('dates')
    solr_uri = request.args.get('uri', 'http://localhost:8983/solr')
    collection = request.args.get('collection', 'posts')

    # Load the query parameters from the JSON file
    query_params = {
        "query": query,
        "fields": "id, title, subreddit, author, score, body, creation_date",
        "params": {
            "defType": "edismax",
            "qf": "title body author subreddit",
            "fq": []
        }
    }

    if subreddits:
        query_params["params"]["fq"].append(f"subreddit:({subreddits})")
    
    if dates:
        date_filters = [f"creation_date:[{year}-01-01T00:00:00Z TO {year}-12-31T23:59:59Z]" for year in dates.split(' OR ')]
        query_params["params"]["fq"].append(" OR ".join(date_filters))

    results = fetch_solr_results(query_params, solr_uri, collection)
    return jsonify(results)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    # Set up argument parsing for the command-line interface
    parser = argparse.ArgumentParser(
        description="Fetch search results from Solr and output them in JSON format."
    )

    # Add arguments for query file, Solr URI, and collection name
    parser.add_argument(
        "--query",
        type=Path,
        required=False,
        help="Path to the JSON file containing the Solr query parameters.",
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="http://localhost:8983/solr",
        help="The URI of the Solr instance (default: http://localhost:8983/solr).",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="posts",
        help="Name of the Solr collection to query (default: 'posts').",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    if args.query:
        # If a query file is provided, fetch results and print them
        with open(args.query, 'r') as file:
            query_params = json.load(file)
        results = fetch_solr_results(query_params, args.uri, args.collection)
        print(json.dumps(results, indent=2))
    else:
        # Run the Flask app
        app.run(debug=True)