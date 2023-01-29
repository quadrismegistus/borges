from .imports import *

def iter_pages(xml_str, page_tag='pb', progress=False):
    xml_str=xml_str.replace(f'<{page_tag}>', f'<{page_tag} >')
    pages = xml_str.split(f'<{page_tag} ')[1:]
    if progress: pages = get_tqdm(pages, position=0)
    for i,page in enumerate(pages):
        if page.startswith('n="'):
            page_n = page[3:].split('"',1)[0]
        else:
            page_n = ''
        page = f'<{page_tag} ' + page + f'</{page_tag}>'
        
        yield {
            'page_num':page_n, 
            'page':html.unescape(page)
        }



class PageObject(BaseObject):
    pass


