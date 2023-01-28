from .imports import *



class BaseCorpus(BaseObject):
    id='corpus'
    name='Corpus'
    col_id='id'

    def __init__(self, **kwargs):
        if kwargs.get('id'): self.id=kwargs['id']
        if kwargs.get('name'): self.name=kwargs['name']
        assert self.name and self.id # can't be empty
        kwargs['name']=self.name
        kwargs['id']=self.id
        super().__init__(**kwargs)

    @property
    def path(self): return os.path.join(PATH_CORPORA, self.id)
    
    @property
    def path_metadata(self): return os.path.join(self.path, self.id+'_metadata.csv')
    @property
    def url_metadata(self): return self.manifest.get('url_metadata')


    @property
    def path_raw(self): return os.path.join(self.path, self.id+'_raw.zip')
    @property
    def url_raw(self): return self.manifest.get('url_raw')

    @cached_property
    def manifest(self): return get_manifest(self.id)

    @property
    def meta(self): return self.metadata()
    @cache
    def metadata(self): 
        self.download_metadata()
        odf=pd.read_csv(self.path_metadata)
        if self.col_id in set(odf.columns):
            odf=odf.set_index(self.col_id)
        return odf
    def download_metadata(self, force=False):
        if self.url_metadata and (force or not os.path.exists(self.path_metadata)):
            zfn=self.path_metadata+'.zip'
            download(self.url_metadata, zfn)
            for fn,content in iter_zip(zfn):
                if fn.endswith('metadata.csv'):
                    with open(self.path_metadata,'wb') as of:
                        of.write(content)
            
            
    


    #######
    # RAW #
    #######
    def download_raw(self, force=False):
        if self.url_raw and (force or not os.path.exists(self.path_raw)):
            download(self.url_raw, self.path_raw)

    def iter_raw(self,force=False,decode=True):
        self.download_raw(force=force)
        yield from iter_zip(self.path_raw,decode=decode)
        