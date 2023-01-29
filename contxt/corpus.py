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
            return True

    def iter_raw(self,force=False,decode=True,**kwargs):
        self.download_raw(force=force)
        yield from iter_zip(self.path_raw,decode=decode,**kwargs)
        

    def install(self):
        solr = get_solr()
        for d in self.compile():
            solr.add(d)




    def compile_raw(self):
        # setup
        if not self.url_metadata or not self.url_raw: 
            log.error(f'url_metadata or url_raw not set')
            return
        self.download_raw()
        unzip(
            self.path_raw, 
            os.path.dirname(self.path_raw)
        )


    @cached_property
    def filenames_raw(self):
        self.compile_raw()

        objs=[]
        for root,dirs,fns in os.walk(os.path.dirname(self.path_raw)):
            for fn in fns:
                if fn.endswith(self.ext_raw):
                    fnfn=os.path.join(root,fn)
                    objs.append(fnfn)
        return objs




    def compile_metadata(self, num_proc=4, lim=None, **kwargs):
        res=pmap(
            self.do_compile_metadata.__func__, 
            self.filenames_raw[:lim],
             num_proc=num_proc, 
             **kwargs
        )
        df=pd.DataFrame(res).set_index(KEY_ID)
        df.to_csv(self.path_metadata)
        return df

    def compile_pages(self, num_proc=4, lim=None, **kwargs):
        pmap(
            self.do_compile_pages.__func__, 
            self.filenames_raw[:lim], 
            num_proc=num_proc,
            **kwargs
        )

    def compile(self, **kwargs):
        self.compile_metadata(**kwargs)
        self.compile_pages(**kwargs)