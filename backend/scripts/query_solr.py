#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path

import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Dictionary to store click counts
click_counts = {}

CLICK_COUNTS_FILE = 'click_counts.csv'

def load_click_counts():
    """Load click counts from a CSV file."""
    global click_counts
    try:
        with open(CLICK_COUNTS_FILE, mode='r') as infile:
            reader = csv.reader(infile)
            click_counts = {rows[0]: int(rows[1]) for rows in reader}
    except FileNotFoundError:
        click_counts = {}

def save_click_counts():
    """Save click counts to a CSV file."""
    with open(CLICK_COUNTS_FILE, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        for post_id, count in click_counts.items():
            writer.writerow([post_id, count])

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

@app.route('/click', methods=['POST'])
def track_click():
    post_id = request.json.get('post_id')
    if post_id:
        if post_id in click_counts:
            click_counts[post_id] += 1
        else:
            click_counts[post_id] = 1
        save_click_counts()  # Save click counts after each update
    return jsonify({"status": "success", "clicks": click_counts.get(post_id, 0)})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    subreddits = request.args.get('subreddits')
    dates = request.args.get('dates')
    sort = request.args.get('sort')
    solr_uri = request.args.get('uri', 'http://localhost:8983/solr')
    collection = request.args.get('collection', 'posts')

    # Load the query parameters from the JSON file
    query_params = {
        "query": query,
        "fields": "id, title, subreddit, author, score, post_score, body, creation_date",
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

    if sort:
        if sort == "date_asc":
            query_params["params"]["sort"] = "creation_date asc"
        elif sort == "date_desc":
            query_params["params"]["sort"] = "creation_date desc"

    results = fetch_solr_results(query_params, solr_uri, collection)

    # Adjust the order based on the new metric
    coefficient = 1.0  # Adjust this coefficient as needed
    for doc in results['response']['docs']:
        post_id = doc['id']
        clicks = click_counts.get(post_id, 0)
        doc['adjusted_score'] = doc['score'] + coefficient * clicks

    # Sort results by the adjusted score
    results['response']['docs'].sort(key=lambda x: x['adjusted_score'], reverse=True)

    return jsonify(results)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    # Load click counts when the server starts
    load_click_counts()

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