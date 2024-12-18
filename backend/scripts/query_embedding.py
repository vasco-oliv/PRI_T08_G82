import json
import requests
from sentence_transformers import SentenceTransformer
import sys

QUERY1 = "I am anxious"
QUERY2 = "I am anxious"
QUERY3 = "depression relationship"
QUERY4 = "coping with stress"

QUERY = [QUERY1, QUERY2, QUERY3, QUERY4]

ROWS = 50

def text_to_embedding(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()
    
    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str

def solr_knn_query(endpoint, collection, embedding):
    url = f"{endpoint}/{collection}/select?rows={ROWS}"

    data = {
        "q": f"{{!knn f=vector topK={ROWS}}}{embedding}",
        "fl": "id, title, subreddit, author, score, post_score, body, creation_date",
        "rows": 50,
        "wt": "json",
        "params": {
            "defType": "edismax",
            "qf": "title^3 body^2 author subreddit^4",
            "pf": "title^3 body^2 author subreddit^4",
            "ps": 5,
            "qs": 5,
            "fq": [],
        }
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def display_results(results):
    docs = results.get("response", {}).get("docs", [])
    if not docs:
        print("No results found.")
        return

    for doc in docs:
        print(f"* {doc.get('id')} {doc.get('title')} [score: {doc.get('score'):.2f}]")

def main():
    query_num = int(sys.argv[1])
    solr_endpoint = "http://localhost:8983/solr"
    collection = "posts"
    
    query_text = QUERY[query_num-1]
    embedding = text_to_embedding(query_text)

    try:
        results = solr_knn_query(solr_endpoint, collection, embedding)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")
        
    print(json.dumps(results, indent=2))
    #display_results(results)

if __name__ == "__main__":
    main()
