from .imports import *

def iter_passages(xml_str):
    import bs4
    dom=bs4.BeautifulSoup(xml_str,'lxml')
    domtags=list(dom())
    for i,tag in enumerate(domtags): tag.i = i
    iterr=get_tqdm(domtags, position=0)
    for i,tag in enumerate(iterr):
        if {tagx.name for tagx in tag.children} == {None}:
            tree_id_tupl=tuple(list(reversed([(x.i,x.name) for x in tag.parents if x.i])) + [(tag.i,tag.name)])
            tree_id_str=' > '.join(f'{x}.{y}' for x,y in tree_id_tupl)
            yield dict(
                tree = tree_id_str,
                tag_i = tag.i,
                tag = tag.name,
                text = tag.text
            )
    