from .imports import *

THREADWORKERS=None
def get_workers(n=NUM_CPU*2):
    global THREADWORKERS
    if THREADWORKERS is None:
        print(f'creating threadpool with {n} workers')
        THREADWORKERS = ThreadPool(n)
    return THREADWORKERS

def stop_workers():
    global THREADWORKERS
    if THREADWORKERS is not None:
        with timer('workers heading home'):
            THREADWORKERS.close()
            THREADWORKERS.join()
            THREADWORKERS = None

def to_bytes(x):
    return str(x).encode() if type(x)!=bytes else x

def compress(data):
    import brotli,base64
    data_zip = brotli.compress(to_bytes(data))
    data_zip_b64=base64.b64encode(data_zip)
    data_zip_b64_str=data_zip_b64.decode()
    return data_zip_b64_str

def decompress(data_zip_b64_str):
    import brotli,base64
    data_zip_b64=to_bytes(data_zip_b64_str)
    data_zip = base64.b64decode(data_zip_b64)
    data = brotli.decompress(data_zip)
    data_str = data.decode()
    return data_str


def hashstr(x):
    import hashlib
    return hashlib.sha224(str(x).encode('utf-8')).hexdigest()

def ishashish(x): 
    return type(x) in {str,bytes} and len(x)==56 and x.isalnum()

def to_nl(x): return x.replace('\r\n','\n').replace('\r','\n')

def oneline(txt):
    return to_nl(txt).replace('\n',' ').replace('  ',' ').strip()

def get_solr(core='contxt_pages'):
    return pysolr.Solr(
        f'http://localhost:8983/solr/{core}/',
        always_commit=True
    )

def get_meta_solr(): return get_solr(core='contxt_metadata')
def get_page_solr(): return get_solr(core='contxt_pages')


def get_tqdm(*args,progress=True,**kwargs):
    if not progress: return get_first(args)
    if 0: #in_jupyter():
        from tqdm.notebook import tqdm as tqdmx
    else:
        from tqdm import tqdm as tqdmx
    return tqdmx(*args,**kwargs)

def in_jupyter(): return sys.argv[-1].endswith('json')


def ensure_dir(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as e:
            print(e)
            log.error(e)

def setup_user():
    ensure_dir(PATH_HOME)

def ensure_link(actual_src,symbolic_link, overwrite=True):
    if os.path.exists(symbolic_link): 
        if not overwrite: return
        os.unlink(symbolic_link)
    os.symlink(
        os.path.abspath(actual_src), 
        os.path.abspath(symbolic_link)
    )


def read_manifests():
    setup_user()

    import configparser
    config = configparser.ConfigParser()
    for fn in os.listdir(PATH_HOME):
        if fn.startswith('manifest'):
            config.read(os.path.join(PATH_HOME,fn))
    
    return {
        corpus:dict(config[corpus].items())
        for corpus in config.keys()
    }

def get_first(l): 
    for x in l: return x
first = get_first


def get_manifest(corpus_name_or_id):
    return get_first(
        cd
        for cname,cd in read_manifests().items()
        if corpus_name_or_id in ({cname} if not cd.get('id') else {cname,cd['id']})
    )



def to_yr(year_str):
    x=''.join(x for x in year_str if x.isdigit())
    return int(x) if x else 0







#!/usr/bin/env python 
__author__  = "github.com/ruxi"
__license__ = "MIT"
def download(url, filename=False, verbose = False, desc=None):
    """
    Download file with progressbar
    """


    import requests 
    from tqdm import tqdm
    import os.path


    if not filename:
        local_filename = os.path.join(".",url.split('/')[-1])
    else:
        local_filename = filename

    ensure_dir(os.path.dirname(local_filename))
    
    r = requests.get(url, stream=True)
    file_size = r.headers.get('content-length')
    chunk = 1
    chunk_size=1024
    num_bars = int(file_size) // chunk_size if file_size else None
    if verbose>0:
        print(dict(file_size=file_size))
        print(dict(num_bars=num_bars))

    
    with open(local_filename, 'wb') as fp:
        iterr=get_tqdm(
            r.iter_content(chunk_size=chunk_size),
            total=num_bars,
            unit='KB',
            desc = local_filename if not desc else desc,
            leave = True
        )
        for chunk in iterr:
            fp.write(chunk)
    return


    



def zeropunc(x,allow={'_'}):
    if not x: return ''
    return ''.join([y for y in x if y.isalnum() or y in allow])





def iter_zip(zipfn, desc='', ext='', decode=True, **kwargs):
    from zipfile import ZipFile
    with ZipFile(zipfn) as zip_file:
        # Iterate through files in zip file
        for zipfilename in get_tqdm(zip_file.filelist, **kwargs):
            if not ext or zipfilename.endswith(ext):
                filecontents = zip_file.read(zipfilename)
                if decode: filecontents=filecontents.decode()
                yield (zipfilename.filename, filecontents)






def unzip(zipfn, dest='.', flatten=False, overwrite=False, replace_in_filenames={},desc='',progress=True):
    from zipfile import ZipFile
    from tqdm import tqdm

    # Open your .zip file
    if not desc: desc=f'Extracting {os.path.basename(zipfn)} to {dest}'
    with ZipFile(zipfn) as zip_file:
        namelist=zip_file.namelist()

        # Loop over each file
        iterr=get_tqdm(iterable=namelist, total=len(namelist),desc=desc) if progress else namelist
        for member in iterr:
            # Extract each file to another directory
            # If you want to extract to current working directory, don't specify path
            filename = os.path.basename(member)
            if not filename: continue
            target_fnfn = os.path.join(dest,member) if not flatten else os.path.join(dest,filename)
            for k,v in replace_in_filenames.items(): target_fnfn = target_fnfn.replace(k,v)
            if not overwrite and os.path.exists(target_fnfn): continue
            target_dir = os.path.dirname(target_fnfn)
            try:
                if not os.path.exists(target_dir): os.makedirs(target_dir)
            except FileExistsError:
                pass
            except FileNotFoundError:
                continue
            try:
                with zip_file.open(member) as source, open(target_fnfn,'wb') as target:
                    shutil.copyfileobj(source, target)
            except FileNotFoundError:
                print('!! File not found:',target_fnfn)



class timer:
    def __init__(self,desc='timer'):
        self.desc=desc
        print(f'{self.desc} ...', end=' ', flush=True)

    def __enter__(self):
        self.now=time.time()
        return self

    def __exit__(self,*x,**y):
        # print(f'{self.desc} elapsed in {round(time.time() - self.now, 1)}s')
        print(f'{round(time.time() - self.now, 2)}s', flush=True)




def clean_text(txt):
    import ftfy,html
    txt=ftfy.fix_text(html.unescape(txt))
    replacements={
        '&eacute':'é',
        '&hyphen;':'-',
        '&sblank;':'--',
        '&mdash;':' -- ',
        '&ndash;':' - ',
        '&longs;':'s',
        '&wblank':' -- ',
        u'\u2223':'',
        u'\u2014':' -- ',
        # '|':'',
        '&ldquo;':u'“',
        '&rdquo;':u'”',
        '&lsquo;':u'‘’',
        '&rsquo;':u'’',
        '&indent;':'     ',
        '&amp;':'&',
        '&euml;':'ë',
        '&uuml;':'ü',
        '&auml;':'ä',
    }
    for k,v in list(replacements.items()):
        if k in txt:
            txt=txt.replace(k,v)
        elif k.startswith('&') and k.endswith(';') and k[:-1] in txt:
            txt=txt.replace(k[:-1],v)
    return txt



def serialize_int(s):
    return int.from_bytes(s.encode(), 'little')

def unserialize_int(n):
    import math
    return n.to_bytes(math.ceil(n.bit_length() / 8), 'little').decode()


def hashint(x): return serialize_int(hashstr(x)[:8])








def _pmap_iter_(func_obj, *args, **kwargs):
    func,obj = func_obj
    res = func(obj, *args, **kwargs)
    return (obj,res)

def pmap_iter(
        func:'function', 
        objs:list, 
        num_proc:int=1, 
        desc:str='',
        progress:bool=True, 
        **tqdm_opts
        ):
    
    from tqdm import tqdm    
    iterr = tqdm(
        total=len(objs), 
        desc=f'{desc} [x{num_proc}]' if num_proc>1 else desc, 
        disable=not progress, 
        **tqdm_opts
    )

    if len(objs)==1 or num_proc==1:
        for obj in objs:
            yield _pmap_iter_((func,obj))
            iterr.update()
    else:
        import multiprocess as mp
        pool = mp.Pool(num_proc)
        funcobjs = [(func,obj) for obj in objs]
        for res in pool.imap_unordered(_pmap_iter_, funcobjs):
            yield res
            iterr.update()

def pmap(*args, **kwargs): return list(pmap_iter(*args,**kwargs))

