import sys
import json
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

FILE_PATH = 'Dataset/dataset'
SEMANTIC_SUFFIX = '_semantic'
FILE_TYPE = '.json'
FORMATTED_SUFFIX = '_formatted'

def format_dataset_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    with open(output_file, 'w') as f:
        f.write("[\n")
        for i, line in enumerate(lines):
            f.write('\t')
            if i != len(lines) - 1:
                f.write(line.strip() + ',\n')
            else:
                f.write(line)
        f.write("]")
    print(f"Formatted file saved at {output_file}")

def get_embedding(text):
    # The model.encode() method already returns a list of floats
    return model.encode(text, convert_to_tensor=False).tolist()

if __name__ == "__main__":
    input_file = f'{FILE_PATH}{FILE_TYPE}'
    formatted_file = f'{FILE_PATH}{FORMATTED_SUFFIX}{FILE_TYPE}'
    output_file = f'{FILE_PATH}{SEMANTIC_SUFFIX}{FILE_TYPE}'
    
    format_dataset_file(input_file, formatted_file)
    
    # Read JSON from STDIN
    with open(formatted_file, 'r') as file:
        data = json.load(file)

    # Update each document in the JSON data
    # Update each document in the JSON data
    total_documents = len(data)
    for idx, document in enumerate(data):
        # Extract fields if they exist, otherwise default to empty strings
        subreddit = document.get("subreddit", "")
        title = document.get("title", "")
        body = document.get("body", "")
        author = document.get("author", "")

        combined_text = subreddit + " " + title + " " + body + " " + author
        document["vector"] = get_embedding(combined_text)
        
        # Print progress only et every 5% of the documents
        if idx % (total_documents // 100) == 0:
            print(f"Processed {round(idx / total_documents * 100,2)}% documents")

    # Output updated JSON to STDOUT
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Semantic embeddings saved at {output_file}")
