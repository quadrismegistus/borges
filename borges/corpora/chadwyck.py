from borges.imports import *
import os,sys; sys.path.insert(0,os.path.abspath('/Users/ryan/github/yapmap'))
from yapmap import *


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


class ChadwyckCorpus(BaseCorpus):
    id='chadwyck'
    name='Chadwyck'
    ext_raw = '.new'

    def compile_metadata(self, num_proc=4, lim=None, **kwargs):
        res=pmap(compile_metadata, self.filenames_raw[:lim], num_proc=num_proc, **kwargs)
        df=pd.DataFrame(res).set_index(KEY_ID)
        df.to_csv(self.path_metadata)


def compile_metadata(fn):
    if not os.path.exists(fn): return
    with open(fn) as f: xml=f.read()
    
    ometa = get_meta_from_raw_xml(xml, fn)
    if 'year' in ometa:            
        ometa['year_str']=str(ometa['year'])
        ometa['year'] = to_yr(ometa['year'])

    get_meta_solr().add(ometa)
    return ometa




def compile_pages(fn):
    if not os.path.exists(fn): return
    with open(fn) as f: xml=f.read()
    text_id=get_id_from_fn(fn)
    solr = get_page_solr()
    for pdx in iter_pages(xml, progress=True):
        pnum=pdx.get('page_num')
        if pnum:
            sdx = {
                KEY_ID:os.path.join(text_id,'page',str(pnum)),
                'text_id':text_id,
                **pdx
            }
            # return sdx
            solr.add(sdx)

    # return ometa
