from .imports import *


@cache
def get_tree_id(tag, bad_tags={'pb'}):
    l=get_tree_id(tag.parent) if tag.parent else []
    if tag.name not in bad_tags and tag.i:
        l.append((tag.i, tag.name))
    return l

def get_tree_id_str(tag):
    l = get_tree_id(tag)
    return ' > '.join(f'{n}.{t}' for n,t in l)



nltkobj = None
def get_nltk():
    global nltkobj
    if nltkobj is None:
        import nltk
        # make sure we have the tokenizer package
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('wordnet')
            nltk.download('omw-1.4')
        nltkobj = nltk
    return nltkobj


def get_dom(xml):
    import bs4,html
    dom=bs4.BeautifulSoup(clean_text(xml))
    domtags=list(dom())
    for i,tag in enumerate(domtags): tag.i = i
    return dom




def Text(x): return TextObject(x)

class TextObject(BaseObject):
    def __init__(self, _id=None):
        self._id=_id



class XMLTextObject(TextObject): pass