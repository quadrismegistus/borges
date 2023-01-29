from contxt.imports import *

def get_meta_from_raw_xml(xml_str,xml_fn):
    md={}
    md[KEY_ID]=get_id_from_fn(xml_fn)

    for line in xml_str.split('\n'):
        #if '<doc>' in line: break

        if '<T1>' in line and not 'title' in md:
            md['title']=line.split('<T1>')[1].split('</T1>')[0]
        if '<ID>' in line and not 'idref' in md:
            md['idref']=line.split('<ID>')[1].split('</ID>')[0]
        if '<A1>' in line and not 'author' in md:
            md['author']=line.split('<A1>')[1].split('</A1>')[0]
        if '<Y1>' in line and not 'year' in md:
            md['year']=line.split('<Y1>')[1].split('</Y1>')[0]
        if '<PBL>' in line and not 'pub' in md:
            md['pub']=line.split('<PBL>')[1].split('</PBL>')[0]
        if '<TY>' in line and not 'type' in md:
            md['type']=line.split('<TY>')[1].split('</TY>')[0]
        if '<attbytes>' in line and not 'name' in md:
            md['name']=line.split('<attbytes>')[0].strip()
        if '</comcitn>' in line: break
    if 'America' in xml_fn:
        md['nation']='American'
    else:
        md['nation']='British'
    md['medium']='Fiction'
    md['subcorpus']=xml_fn.split(os.path.sep)[-2]
    md['fn_raw']=os.path.sep.join(xml_fn.split(os.path.sep)[-2:])
    return {str(k):str(v) for k,v in md.items()}


def get_id_from_fn(fn):
    fn_raw=os.path.sep.join(fn.split(os.path.sep)[-2:])
    return f'_{ChadwyckCorpus.id}/{os.path.splitext(fn_raw)[0]}'


def read_xml(fn):
    if not os.path.exists(fn): return ''
    with open(fn) as f: xml=f.read()
    xml = html.unescape(xml)
    return xml
    

def do_compile_metadata(fn):
    xml = read_xml(fn).split('<body>')[0]
    if not xml: return {}

    ometa = get_meta_from_raw_xml(xml, fn)
    if 'year' in ometa:            
        ometa['year_str']=str(ometa['year'])
        ometa['year'] = to_yr(ometa['year'])

    DB().metadata.replace_one({KEY_ID:ometa[KEY_ID]}, ometa, upsert=True)
    return ometa




def do_compile_pages(fn):
    if not os.path.exists(fn): return
    with open(fn) as f: xml=f.read()
    text_id=get_id_from_fn(fn)
    # solr = get_page_solr()
    coll = DB().pages
    # sld=[]
    for pdx in iter_pages(xml, progress=False):
        pnum=pdx.get('page_num')
        if pnum:
            _id=os.path.join(text_id,'page',str(pnum))
            sdx = {
                KEY_ID:_id,
                'text_id':text_id,
                **pdx
            }
            coll.replace_one({'_id':_id}, sdx, upsert=True)



class ChadwyckCorpus(BaseCorpus):
    id='chadwyck'
    name='Chadwyck'
    ext_raw = '.new'
    do_compile_metadata = do_compile_metadata
    do_compile_pages = do_compile_pages
