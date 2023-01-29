from .imports import *

def get_solr(core='borges_pages'):
    return pysolr.Solr(
        f'http://localhost:8983/solr/{core}/',
        always_commit=True
    )

def get_meta_solr(): return get_solr(core='borges_metadata')
def get_page_solr(): return get_solr(core='borges_pages')


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



class BaseObject(object):
    @property
    def data(self): return self.__getattribute__('_data')

    def __getattr__(self, __name: str) -> Any:
        try:
            if __name in self.data: return self.data[__name]
            return super().__getattr__(__name)
        except AttributeError:
            return None

    def __init__(self, *args, **kwargs):
        self._data={**kwargs}


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