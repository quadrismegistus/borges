from .imports import *

def tokenize_sents(txt):
    #return get_nltk().sent_tokenize(txt)
    from flair.tokenization import split_multi
    return split_multi(txt)

def iter_sents_xml(xml, para_tag='p', sent_tag='s', progress=False):
    dom=get_dom(xml)
    para_i=0
    sent_i=0
    paras=dom(para_tag)
    if progress: paras=get_tqdm(list(paras), position=0, desc='Iterating paragraphs')
    for para in paras:
        # para_tree = get_tree_id(para)
        sents = [s for s in para(sent_tag)]
        if not sents:
            sents=tokenize_sents(para.text)
        for sent in sents:
            sent_str = oneline(sent if type(sent)==str else sent.text)
            # xml_tree = para_tree if type(sent)==str else get_tree_id(sent)
            yield {
                'para_i':para_i,
                'sent_i':sent_i,
                # 'xml_tree': xml_tree,
                'sent':sent_str
            }
            para_i+=1
            sent_i+=1




def iter_sents_in_str(string):
    string = clean_text(string).strip()
    lines = '\n'.join([ln.strip() for ln in string.split('\n')])
    paras = list(lines.split('\n\n'))
    si=0
    pi=0
    for para in paras:
        thisparaadded=False
        for sent in tokenize_sents(para.strip()):
            words=sent.split()
            numalw = [w for w in words if w.isalpha()]
            if numalw and set(sent.lower())-{'i','v','x'}:  # to remove bogus lines, require at least one token in line to be entirely alphabet-composed and even then for there to be more letters present than the common roman numerals of i,v,x
                yield dict(
                    para_i=pi, 
                    sent_i=si,
                    sent=oneline(sent)
                )
                si+=1
                thisparaadded=True
        if thisparaadded:
            pi+=1
        



def iter_sents(progress=True, lim=None, as_obj=True,**kwargs):
    coll=DB().sents_text
    sents=coll.find()
    if progress:
        sents=get_tqdm(
            sents, 
            total=coll.count_documents({}) if not lim else lim,
            **kwargs
        )
    done=set()
    for sent_d in sents:
        sent_str=sent_d.get('sent')
        if sent_str and sent_str not in done:
            done.add(sent_str)
            yield sent_str if not as_obj else Sent(sent_str)


def Sent(id_or_d):
    if not id_or_d: return

    # already sent?
    if isinstance(id_or_d, SentenceObject): return id_or_d

    # strings
    if type(id_or_d) == str:
        if '/sent/' in id_or_d:
            d = DB().sents_text.find_one(id_or_d)
            if d: return TextSentenceObject(**d)
        else:
            return SentenceObject(sent=id_or_d)
    
    if type(id_or_d) == dict:
        if 'text_id' in id_or_d:
            return TextSentenceObject(**d)
        if 'sent' in id_or_d:
            return SentenceObject(**d)





class SentenceObject(BaseObject):
    def __str__(self): return self.sent
    def __repr__(self):
        # return f'<Sent: {oneline(self.sent)}>'
        return f'📎{oneline(self.sent)}📎'
    @cached_property
    def db(self): return DB().sents_nlp

    @cached_property
    def flair(self):
        from flair.data import Sentence
        return Sentence(self.sent)

    @cached_property
    def tokens(self):
        return [tok.text for tok in self.flair]

    @cache
    def token_embedding(self, **kwargs): return TokenEmbedding()
    @cache
    def embedding(self, **kwargs): return SentenceEmbedding()
    
    def embed(self, **kwargs):
        return self.embedding(**kwargs).embed(self, **kwargs)
    def embed_tokens(self, **kwargs):
        return self.token_embedding(**kwargs).embed(self, **kwargs)
    
    def nearest(self, **kwargs):
        return self.embedding(**kwargs).nearest(self, **kwargs)
    def nearby(self, **kwargs):
        return self.embedding(**kwargs).nearby(self, **kwargs)
    

class TextSentenceObject(SentenceObject):
    @cached_property
    def db(self): return DB().sents_text







def do_embed_sent(sent):
    embed_list = Sent(sent).embed(save=False, force=True, as_list=True)
    return (str(sent),embed_list)


def embed_sents(lim=10, num_proc=1, shuffle=True, desc='Embedding known sentences', **kwargs):
    sents = list(islice(iter_sents(as_obj=False,desc='Gathering known sentences'), lim * 100 if lim else None))
    
    e = SentenceEmbedding()
    get_workers()

    for (sent,embed) in pmap_iter(
            do_embed_sent, 
            sents, 
            num_proc=num_proc, 
            shuffle=shuffle, 
            lim = lim,
            desc = desc,
            # kwargs=dict(embedding_model=e),
            use_threads=True,
            **kwargs
            # use_torch=True
            ):
        
        e.save_embed(sent, embed)
    
    stop_workers()




def do_embed_tokens(sent):
    Sent(sent).embed_tokens(save=True, force=True)

def embed_tokens(sents=None, lim=10, num_proc=1, shuffle=True, desc='Embedding known sentences', **kwargs):
    sents = list(islice(iter_sents(as_obj=False,desc='Gathering known sentences'), lim * 100 if lim else None)) if not sents else sents
    get_workers()
    pmap(
        do_embed_tokens, 
        sents,
        num_proc=num_proc, 
        shuffle=shuffle, 
        lim = lim,
        desc = desc,
        # kwargs=dict(embedding_model=e),
        use_threads=True,
        **kwargs
        # use_torch=True
    )
    stop_workers()