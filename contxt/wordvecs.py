from .imports import *

FN_MODEL='model.txt.gz'
FN_MODEL_SYMLINK='training.txt'
FN_MODEL_VOCAB='vocab.txt'
FN_MODEL_PARAMS='params.json'


class Word2Vex:
    DATA_DIR_NAME='word2vex'
    DEFAULT_GENSIM_OPTS = dict(
        vector_size=100,
        alpha=0.025,
        window=5,
        min_count=5,
        max_vocab_size=None,
        sample=0.001,
        seed=1,
        workers=3,
        min_alpha=0.0001,
        sg=0,
        hs=0,
        negative=5,
        ns_exponent=0.75,
        cbow_mean=1,
        epochs=5,
        null_word=0,
        trim_rule=None,
        sorted_vocab=1,
        batch_words=10000,
        compute_loss=False,
        callbacks=(),
        comment=None,
        max_final_vocab=50000,  # only one not default
        shrink_windows=True,
    )

    def __init__(self, corpus_file, id=None, output_path=None, **gensim_opts):
        self.corpus_file = os.path.abspath(corpus_file)
        self.fn = os.path.basename(self.corpus_file)
        self.id = id if id else os.path.splitext(self.fn)[0]
        if self.id.startswith('data.'): self.id=self.id[5:]
        self.gensim_opts = {**self.DEFAULT_GENSIM_OPTS, **gensim_opts}
        self.output_path = output_path if output_path else os.path.join(PATH_DATA, self.DATA_DIR_NAME, self.id)

        # ensure?
        ensure_dir(self.output_path)
        ensure_link(
            self.corpus_file, 
            os.path.join(self.output_path, 'corpus.txt'),
            overwrite=False
        )
    
    def get_path_model_run(self, run = 1, method='word2vec'):
        opath = os.path.join(
            self.output_path, 
            method,
            f'run_{run:02}',
        )
        return opath

    def train(self, n=5, force=False, num_proc=1, method='word2vec', **opts):
        funcname='do_train_'+method
        assert hasattr(Word2Vex, funcname)

        func = getattr(Word2Vex,'do_train_'+method)

        opts = {**self.gensim_opts, **opts}
        objs = [
            (
                self.corpus_file, 
                self.get_path_model_run(run+1, method=method),
                force,
                opts
            )
            for run in range(n)
        ]
        return pmap(
            func, 
            objs, 
            num_proc=num_proc,
            desc=f'Training {n} word2vec models'
        )









    ##### utils
    def train_word2vec(
            corpus_file, 
            output_dir=None, 
            save_file=True, 
            save_db=True,
            force_file=False,
            force_db=False,
            **opts):
        
        import gensim
        model_fn = os.pat
        kvecs = gensim.models.word2vec.Word2Vec(
            corpus_file=corpus_file,
            **opts
        ).wv
        
        if output_dir and save_file:
            Word2Vex.save_word2vec_file(kvecs, output_dir, corpus_file, opts)
        
        if save_db:
            Word2Vex.save_word2vec_db(kvecs)

        return kvecs

    def save_word2vec_file(kvecs, output_dir, corpus_file, params):
        ensure_dir(output_dir)
        opath_model = os.path.join(output_dir, FN_MODEL)
        opath_symlink = os.path.join(output_dir, FN_MODEL_SYMLINK)
        opath_vocab = os.path.join(output_dir, FN_MODEL_VOCAB)
        opath_params = os.path.join(output_dir, FN_MODEL_PARAMS)

        # save model and vocab
        kvecs.save_word2vec_format(opath_model, opath_vocab, binary=False)
        
        # save params
        with open(opath_params,'w') as of: json.dump(params, of, indent=2)

        # save symlink
        ensure_link(corpus_file, opath_symlink, overwrite=True)

        return kvecs

    def do_train_word2vec(obj): 
        corpus_file,output_dir,force,opts = obj
        if force or not os.path.exists(output_dir):
            Word2Vex.train_word2vec(corpus_file, output_dir=output_dir, **opts)
        return os.path.join(output_dir, FN_MODEL')
        

        
        
