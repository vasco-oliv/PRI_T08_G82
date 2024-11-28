import sys
import json
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

FILE_PATH = '../Dataset/dataset.json'

def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    # Read JSON from STDIN
    with open(FILE_PATH, 'r') as file:
        data = json.load(file)

    # Update each document in the JSON data
    for document in data:
        # Extract fields if they exist, otherwise default to empty strings
        subreddit = document.get("subreddit", "")
        title = document.get("title", "")
        body = document.get("body", "")
        author = document.get("author", "")

        combined_text = subreddit + " " + title + " " + body + " " + author
        document["vector"] = get_embedding(combined_text)

    # Output updated JSON to STDOUT
    with open(FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
