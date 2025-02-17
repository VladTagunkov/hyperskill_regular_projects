# Your code here
from qdrant_client import QdrantClient,models
import json
from typing import Any, Generator
import uuid
from qdrant_client.models import PointStruct
from itertools import islice
import time
import openai
from dotenv import load_dotenv
import re
from fastapi import FastAPI
from typing import Optional, List, Dict
from pydantic import BaseModel

######################PART1#################################

load_dotenv()


qdrant_client = QdrantClient(host="localhost", port=6333)
openai_client = openai.OpenAI(
    base_url="https://litellm.aks-hs-prod.int.hyperskill.org",
)
COLLECTION_NAME = 'arxiv_papers'
EMBEDDING_MODEL = "text-embedding-ada-002"
VECTORS_CONFIG = {"size": 1536, "distance": "Cosine"}

DATA_FILE_PATH = 'ml-arxiv-embeddings.json'

if not qdrant_client.collection_exists(collection_name=f"{COLLECTION_NAME}"):
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VECTORS_CONFIG
    )

def stream_json(file_path) -> Generator[Any, Any, None]:
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def batch_maker(iterable, batch_size):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch

json_data = stream_json(DATA_FILE_PATH)
batch_size = 500

def qdrant_data_loader(json_data,batch_size):
    iteration_number = 0
    for batch in batch_maker(json_data, batch_size):
        try:
            ids = [str(uuid.uuid5(namespace=uuid.NAMESPACE_DNS, name=point.get("id"))) for point in batch]
            vectors = [point.pop('embedding') for point in batch if point['embedding'] is not None]
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=models.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=batch,
                ),
            )
            print(f'Iteration {iteration_number} pass!')
            iteration_number += 1
        except Exception as e:
            print(e)

start_time = time.time()
qdrant_data_loader(json_data, batch_size)
print("--- %s seconds ---" % (time.time() - start_time))

####################PART2#################################

doc_name = "Gromov-Hausdorff stability of linkage-based hierarchical clustering methods"
doc_id = "1311.5068"

hits = qdrant_client.scroll(
    collection_name=COLLECTION_NAME,
    scroll_filter=models.Filter(
        must=[
            models.FieldCondition(key="id", match=models.MatchValue(value=doc_id)),
        ]
    ),
    limit=5,
    with_payload=True,
    with_vectors=True,
)

master_vector = hits[0][0].vector

def get_query_points(_qdrant_client,query_vector,limit=5):
    vector_hits = _qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    ).points
    return vector_hits

query_points_p2 = get_query_points(qdrant_client,master_vector)
def closest_id_retriever(query_points):
    final_list = []
    for vector_hit in query_points:
        final_list.append(vector_hit.payload['id'])
    return final_list

part2_id_list = closest_id_retriever(query_points_p2)
print(part2_id_list)

##########################PART3######################
openai_client = openai.OpenAI(
    base_url="https://litellm.aks-hs-prod.int.hyperskill.org",
)
user_query = "the attention mechanism in deep learning"

def get_embedding(_client,query):
    response = _client.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

user_query_embedding = get_embedding(openai_client,user_query)
query_points_p3 = get_query_points(qdrant_client,user_query_embedding)

part3_id_list = closest_id_retriever(query_points_p3)
print(part3_id_list)
# ###################PART4######################
user_query_part4 = "Mentions of point clouds by Tian-Xing Xu"

def author_extractor(query):
    pattern = r"by\s+([A-Za-z\s\-]+)"
    full_name = re.findall(pattern,query)[0]
    if full_name=='':
        return None
    else:
        return full_name

autor = author_extractor(user_query_part4)
def get_query_points_author(_qdrant_client,query_vector,author,limit=5):
    vector_hits = _qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="authors", match=models.MatchText(text=author))],
        ),
        limit=limit,
    ).points
    return vector_hits

def find_document_id_part_4(_author,_openai_client,_qdrant_client,_query,limits = 3):
    if _author is not None:
        query_embedding = get_embedding(_openai_client, _query)
        query_points = get_query_points_author(_qdrant_client,query_embedding,_author,limit=limits)
        final_closest_id = closest_id_retriever(query_points)
    else:
        query_embedding = get_embedding(_openai_client,_query)
        query_points = get_query_points(_qdrant_client,query_embedding,limit=limits)
        final_closest_id = closest_id_retriever(query_points)
    return final_closest_id

final_list_p4 = find_document_id_part_4(autor,openai_client,qdrant_client,user_query_part4)
#print(final_list_p4)
####################PART5###############################

app = FastAPI()

def find_query_points_5(_author,_openai_client,_qdrant_client,_query,limits = 3):
    if _author is not None:
        query_embedding = get_embedding(_openai_client, _query)
        query_points = get_query_points_author(_qdrant_client,query_embedding,_author,limit=limits)
        #final_closest_id = closest_id_retriever(query_points)
    else:
        query_embedding = get_embedding(_openai_client,_query)
        query_points = get_query_points(_qdrant_client,query_embedding,limit=limits)
        #final_closest_id = closest_id_retriever(query_points)
    return query_points

class SearchRequest(BaseModel):
    """
    Model representing a search request sent by a client.

    Attributes:
        query (str): The search query string provided by the client.
        top_n (Optional[int]): The number of top search results to return.
            Defaults to 5 if not provided.
    """
    query: str
    top_n: Optional[int] = 5

class SearchResult(BaseModel):
    """
    Model representing an individual search result.

    Attributes:
        id (str): Unique identifier for the search result item.
        payload (Dict): A dictionary containing additional data or metadata about the item.
        score (float): The relevance score of the search result, typically used for ranking.
    """
    id: str
    payload: Dict
    score: float

class SearchResponse(BaseModel):
    """
    Model representing the response returned to a client after a search.

    Attributes:
        results (List[SearchResult]): A list containing the top matching search results.
    """
    results: List[SearchResult]

@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    query = request.query
    top_n = request.top_n
    autor = author_extractor(query)
    query_points = find_query_points_5(autor, openai_client, qdrant_client, query, limits=top_n)
    result_search = {"results": []}
    for point in query_points:
        tmp_res = {"id": point.id, "payload": point.payload, "score": point.score}
        if len(result_search["results"]) == 0:
            result_search["results"] = [tmp_res]
        else:
            tmp_list = result_search["results"]
            tmp_list.append(tmp_res)
            result_search["results"] = tmp_list
    return result_search