from .imports import *

DEFAULT_SENTEMBED_METHOD='sentence-transformers'
# DEFAULT_SENTEMBED_MODEL='all-MiniLM-L6-v2'
DEFAULT_SENTEMBED_MODEL='all-mpnet-base-v2'
# DEFAULT_SENTEMBED_MODEL='paraphrase-MiniLM-L3-v2'
# DEFAULT_SENTEMBED_MODEL='sentence-t5-xxl'
# DEFAULT_SENTEMBED_MODEL='all-roberta-large-v1'




@cache
def SentenceEmbedding(model=DEFAULT_SENTEMBED_MODEL, method=DEFAULT_SENTEMBED_METHOD):
    name=f'{method}__{model}' if method else model
    embedding=None
    
    if method.startswith('sentence-transform'):
        from flair.embeddings import SentenceTransformerDocumentEmbeddings
        embedding = SentenceTransformerDocumentEmbeddings(model)
    
    if name and embedding:
        return SentenceEmbeddingObject(name=name, embedding=embedding)



@cache
def TokenEmbedding(
        flair_models='', 
        # flair_models='multi-forward multi-backward', 
        transformer_models='bert-base-multilingual-cased'
        # transformer_models='bert-base-multilingual-cased emanjavacas/MacBERTh'
    ):
    from flair.embeddings import FlairEmbeddings, TransformerWordEmbeddings, StackedEmbeddings

    return TokenEmbeddingObject(
        name=f'flair_{flair_models}__transformer_{transformer_models}',
        embedding=StackedEmbeddings(
            embeddings=[
                FlairEmbeddings(mname) for mname in flair_models.split()
            ] + [
                TransformerWordEmbeddings(mname) for mname in transformer_models.split()
            ]
        )
    )




class EmbeddingObject:
    def __init__(self, name, embedding):
        self.name = name
        self.embedding = embedding

    @cached_property
    def num_dims(self):
        return self.embedding.embedding_length

    @cached_property
    def vdb(self):
        return VectorDB(name=self.name, num_dims=self.num_dims)

    def nearest(self, sent):
        for sent in self.nearby(sent, n=1): return sent

class TokenEmbeddingObject(EmbeddingObject):
    def embed(self, sent, save=True, force=False):
        # res in db?
        # # get new
        from .sent import Sent
        sent=Sent(sent)
        sentnlp=sent.flair
        numtoks = len(sentnlp)
        def _key(i): return f'{i+1:06}__{sent.tokens[i]}__{sent}'
        keytoks = [_key(i) for i in range(numtoks)]
        inames=('sent','tok_i','tok')

        if not force:
            res_l=[
                self.vdb.get(tok_key,{}).get('_source',{}).get('vec')
                for tok_key in keytoks
            ]
            if not any(x is None for x in res_l) and len(res_l) == len(sent.tokens):
                idata=[(sent.sent, i+1, token) for i,token in enumerate(sent.tokens)]
                return pd.DataFrame(res_l, index=pd.MultiIndex.from_tuples(idata,names=inames))

        # otherwise... create!
        self.embedding.embed(sentnlp)
        indices=[]
        rows=[]
        for i,token in enumerate(sentnlp):
            token_index = _key(i)
            token_embed = token.embedding.tolist()
            if token_index and token_embed:
                self.vdb.set(token_index,token_embed)
                indices.append((sent.sent, i+1, token.text))
                rows.append(token_embed)
        df = pd.DataFrame(rows, index=pd.MultiIndex.from_tuples(indices, names=inames))
        return df


class SentenceEmbeddingObject(EmbeddingObject):
    def save_embed(self, sent, embed):
        l=embed.tolist() if hasattr(embed,'tolist') else list(embed)
        self.vdb.set(sent, l)

    def embed(self, sent, save=False, force=False, as_array=False, as_list=False, as_df=True):
        # res in db?
        l=[]
        if not force:
            l=self.vdb.get(sent,{}).get('_source',{}).get('vec',[])
        if not l:
            # get new
            from .sent import Sent
            res = self.embedding.embed(Sent(sent).flair)
            res_embed = res[0].get_embedding() if res else None
            l=res_embed.tolist()
            if save: self.save_embed(sent,l)

        if as_list: return l
        if as_array: return np.array(l)
        if as_df: return pd.DataFrame([l], index=[str(sent)]).rename_axis('sent')
        return l

    def nearby(self, sent, n=3, **kwargs):
        evec = self.embed(sent, as_array=True, save=False)
        from .sent import Sent
        return [
            (Sent(d.get('_source',{}).get('sent')), d.get('_score',np.nan))
            for d in self.vdb.nearby(evec, n=n+1, **kwargs)
            if d.get('_source',{}).get('sent') != str(sent)
        ][:n]


