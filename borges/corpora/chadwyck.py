from borges.imports import *

def get_meta_from_raw_xml(xml_str,xml_fn):
    md={}
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
    return md