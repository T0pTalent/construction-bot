import pinecone
import openai
import uuid
import json
from config import *
from openai.embeddings_utils import get_embedding
from langchain.text_splitter import CharacterTextSplitter


openai.api_key = OPENAI_KEY
embedding_model = "text-embedding-ada-002"
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

def embedding(sentences):
    if isinstance(sentences, str):
        return get_embedding(sentences, engine=embedding_model)
    elif isinstance(sentences, list):
        result = []
        for sentence in sentences:
            result.append(get_embedding(sentence, engine=embedding_model))
        return result
    
def upsert_pinecone(index, data):
    item_ids = []
    embeddings = []
    metadata = []

    for record in data:
        embeddings.append(record["embedding"])
        item_ids.append(str(uuid.uuid4()))
        metadata.append(record["metadata"])

    records = zip(item_ids, embeddings, metadata)
    upsert_results = index.upsert(vectors=records)
    return upsert_results

def read_data(fpath):
    with open(fpath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    keys = list(data.keys())
    values = list(data.values())
    
    new_data = []
    for i in range(len(data)):
        new_data.append({
            'metadata': {'question': keys[i], 'answer': values[i]},
            'text': keys[i] + values[i],
            'embedding': embedding(keys[i] + '\n' + values[i])
        })
    
    return new_data

# def temp():
#     index = pinecone.Index('test')
#     data = read_data('data/data.json')
#     upsert_pinecone(index, data)

# temp()