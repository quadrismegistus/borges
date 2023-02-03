from .imports import *
DEFAULT_DB='contxt'

def upsert(coll, value, id_key='_id'):
    if not id_key in value or not value[id_key]: return
    try:
        coll.insert_one(value)
        # print('new!',value['_id'])
    except DuplicateKeyError:
        coll.replace_one({id_key:value[id_key]}, value, upsert=True)
        # print('edited',value['_id'])



@cache
def DB(db=DEFAULT_DB): return DataDB(db)

class DataDB(BaseObject):
    def __init__(self, db=DEFAULT_DB): 
        self._dbname=db

    def __enter__(self):
        self.client
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    @cached_property
    def client(self): return MongoClient()
    @cached_property
    def db(self): return self.client[self._dbname]
    
    @cached_property
    def metadata(self): 
        coll=self.db['metadata']
        coll.create_index('year')
        coll.create_index('author')
        coll.create_index([('title', 'text')])
        return coll
    
    @cached_property
    def pages(self): 
        coll=self.db['pages']
        coll.create_index('text_id')
        coll.create_index('page_num')
        coll.create_index([('page', 'text')])
        return coll


    @cached_property
    def sents_text(self): 
        coll=self.db['sents_text']
        coll.create_index('text_id')
        coll.create_index('corpus_id')
        coll.create_index('sent_id')
        coll.create_index([('sent', 'text')])
        return coll

    def search_sents(self, term_or_phrase):
        return pd.DataFrame(self.sents_text.find({'$text':{'$search':term_or_phrase}}))

    @cached_property
    def sents_nlp(self): 
        coll=self.db['sents_nlp']
        return coll

    @cache
    def sents_embedding(self, model, method=''):
        key=f'{method}__{model}' if method else model
        dbkey=f'sents_embedding_{key}'
        coll=self.db[dbkey]
        return coll

    @cached_property
    def sents_key(self): 
        coll=self.db['sents_key']
        coll.create_index('sent')
        return coll

    # @cache
    # def cache(self, name):
    #     from sqlitedict import SqliteDict
    #     return SqliteDict()





class MongoDict(UserDict):
    def __init__(self, collection, db=DEFAULT_DB):
        self.name=collection
        self.db=DB(db).db[collection]

    def __getitem__(self, key):
        res=self.db.find_one(key)
        if res: return res.get('val')
    
    def __setitem__(self, key, val):
        upsert(self.db, {'_id':key, 'val':val})


class HashDict:
    def __init__(self, id='contxt_hasher'):
        self.db=MongoDict('hashtable', db=id)
    
    def __getitem__(self, sent_or_hash): return self.get(sent_or_hash)
    def __call__(self, sent_or_hash): return self.get(sent_or_hash)

    def get(self, sent_or_hash):
        sent_or_hash = str(sent_or_hash)
        if not ishashish(sent_or_hash):
            # sent to hash
            skey=hashstr(sent_or_hash)
            self.db[skey]=str(sent_or_hash)
            return skey
        else:
            # hash to sent
            return self.db[sent_or_hash]
H=Hasher=HashDict()










## adapted from https://github.com/Zenika/elasticsearch-semantic-search/blob/c7cbfea6de22b3af2d050ba115c0d11ba3b1f8b2/es/esFunctions.py

from elasticsearch import NotFoundError

def get_eclient():
    from elasticsearch import Elasticsearch
    client = Elasticsearch('http://localhost:9200')
    return client

def get_eclient_async():
    from elasticsearch import AsyncElasticsearch
    client = AsyncElasticsearch('http://localhost:9200')
    return client


def _index_exists(client, index_name): 
    return client.indices.exists(index=index_name)

def define_sentvec_index(index_name, num_dims, delete_index=True, client=None):
    client=get_client() if client is None else client
    if not delete_index and _index_exists(client, index_name): return
    client.indices.delete(index=index_name, ignore=[404], request_timeout=60)
    index_definition = {
    
        # "settings": {
            # "number_of_shards": 1,
            # "number_of_replicas": 1
        # },
        "mappings": {
            "properties": {
                "sent": {
                    "type": "text",
                    "index": False
                },
                "vec": {
                    "type": "dense_vector",
                    "dims": num_dims
                }
            }
        }
    }
    print("create index", index_name, "definition", index_definition)
    client.indices.create(index=index_name, body=index_definition)











class VectorDB(BaseObject):
    def __init__(self, name, num_dims, delete_index=False):
        self.name=f'{name}__{num_dims}dim'.lower()
        self.num_dims=num_dims
        self.delete_index=delete_index

    def clear(self, delete_index=True):
        if delete_index and _index_exists(self.client, self.name):
            self.client.indices.delete(
                index=self.name, 
                ignore=[404], 
                request_timeout=60
            )
    
    @cached_property
    def index(self):
        define_sentvec_index(
            index_name=self.name,
            num_dims=self.num_dims, 
            delete_index=self.delete_index, 
            client=self.client
        )
        return partial(self.client.index, index=self.name)
    
    @cached_property
    def client(self): return get_eclient()

    def set(self, sent, vec):
        try:
            def task(): 
                self.index(id=hashstr(sent), body={'sent':str(sent), 'vec':vec})
            # def whendone(x): print('done!!',flush=True)
            get_workers().apply_async(task)#, callback=whendone)
        except Exception as e:
            raise e

    def get(self, sent, default=None):
        from elasticsearch import NotFoundError
        try:
            return self.client.get(index=self.name, id=hashstr(sent))
        except NotFoundError:
            return default
    
    def has(self, sent):
        from elasticsearch import NotFoundError
        try:
            self.client.get(index=self.name, id=hashstr(sent))
            return True
        except NotFoundError:
            return False

    def nearby(self, vec, n=1):
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, doc['vec']) + 1.0",
                    "params": {"query_vector": list(vec)}
                }
            }
        }
        res = self.client.search(
            index=self.name,
            body={
                "size": n,
                "query": script_query,
                # "_source": {"includes": ["title", "body"]}
            },
            request_timeout=60
        )
        hits = dict(res).get('hits',{}).get('hits',[])
        return [
            (d.get('_source',{}).get('sent'), d.get('_score',np.nan))
            for d in hits
        ][:n]














from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Match
from qdrant_client.http.exceptions import UnexpectedResponse

class QdrantVectorDB(BaseObject):
    def __init__(self, name, num_dims, host='localhost', port=6333, **kwargs):
        self.name=f'{name}__{num_dims}dim'.lower()
        self.num_dims=num_dims
        self.host=host
        self.port=port


    @cached_property
    def client(self):
        client = QdrantClient(host=self.host, port=self.port)
        try:
            client.http.collections_api.get_collection(self.name)
        except UnexpectedResponse:
            client.recreate_collection(
                collection_name=self.name,
                vectors_config=VectorParams(size=self.num_dims, distance=Distance.COSINE),
            )
        return client

    def set(self, sent, vec):
        sent = str(sent)
        id = hashint(sent)
        self.client.upsert(
            collection_name=self.name,
            points=[PointStruct(id=id, payload={'sent':sent}, vector=list(vec))],
            wait=False
        )

    def get(self, sent, default=None):
        sent = str(sent)
        res = self.client.retrieve(
            collection_name=self.name,
            ids=[hashint(sent)],
            with_payload=False,
            with_vectors=True
        )
        # return res[0].vector if res and hasattr(res[0],'vector') else default
        return res if res else default
    
    def has(self, sent):
        return self.get(sent,default=None) is not None

    def nearby(self, vec, n=3):
        hits = self.client.search(
            collection_name=self.name,
            query_vector=list(vec),
            # append_payload=True,  # Also return a stored payload for found points
            limit=n+1  # Return 5 closest points
        )
        return [
            (hit.payload.get('sent'), hit.score)
            for hit in hits
            if hit.score < 1.0  ## no exact matches
        ][:n]