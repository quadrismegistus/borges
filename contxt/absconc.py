from .imports import *
URL_WORDNORM='https://www.dropbox.com/s/o4vcjj9hmqhtcgi/data.allnorms.pkl.gz?raw=1'
PATH_WORDNORM=os.path.join(PATH_DATA, 'data.allnorms.pkl.gz')
PATH_WORDSCORE_PERC=os.path.join(PATH_DATA, 'data.allnorms.scores_perc.json')
PSG_LEN=50

def tokenize(txt):
    import re
    return re.findall(r"[\w']+|[.,!?; -—–\n]", txt)

def untokenize(words):
    """
    Untokenizing a text undoes the tokenizing operation, restoring
    punctuation and spaces to the places that people expect them to be.
    Ideally, `untokenize(tokenize(text))` should be identical to `text`,
    except for line breaks.
    """
    text = ' '.join(words)
    step1 = text.replace("`` ", '"').replace(" ''", '"').replace('. . .', '...')
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't").replace(
        "can not", "cannot")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()







@cache
def get_absconc_wordnorms_raw():
    if not os.path.exists(PATH_WORDNORM): download(URL_WORDNORM, PATH_WORDNORM)
    return pd.read_pickle(PATH_WORDNORM)

@cache
def get_absconc_wordnorms(key_contains=''):
    normdf=get_absconc_wordnorms_raw()
    if key_contains: normdf = [[c for c in normdf if key_contains in c]]
    return normdf

@cache
def get_absconc_wordscores(key_contains=''):
    scores = get_absconc_wordnorms(key_contains=key_contains).median(axis=1)
    return dict(zip(scores.index, scores))

@cache
def get_absconc_wordscores_perc(key_contains='', force=False):
    path=os.path.splitext(PATH_WORDSCORE_PERC)[0] + ('.' + key_contains if key_contains else '') + os.path.splitext(PATH_WORDSCORE_PERC)[-1]
    if force or not os.path.exists(path):
        scores_d = get_absconc_wordscores(key_contains=key_contains)
        scores_arr = np.array(list(scores_d.values()))
        def getperc(w): return percentileofscore(scores_arr, scores_d[w]) * 100
        words=list(sorted(scores_d.keys(), key=lambda w: scores_d[w]))
        d=dict(zip(words, pmap_iter(getperc, words, use_threads=True, num_proc=1)))
        ensure_dir(os.path.dirname(path))
        with open(path,'w') as of: json.dump(d, of)
    else:
        with open(path,'r') as f: d=json.load(f)
    return d

def _get_psg_info(psg_tokens, df_key='psg_txt'):
    word2score=get_absconc_wordscores()
    # word2perc=get_absconc_wordscores_perc()
    bucket = psg_tokens
    psg_str = ''.join(bucket)
    # found_words = [w.lower() for w in bucket if w.lower() in set(word2perc.keys())&set(word2score.keys())]
    found_words = [w.lower() for w in bucket if w.lower() in word2score]
    found_words_scores = [word2score[w] for w in found_words]
    found_words_str = '; '.join(f'{w} ({word2score[w]:.3})' for w in found_words)
    return {
        df_key:psg_str,
        'psg_num_tokens':len([w for w in bucket if w.strip()]),
        'psg_num_words':len([w for w in bucket if w and w[0].isalpha()]),
        'absconc_words_median':np.median(found_words_scores),
        'absconc_words_mean':np.mean(found_words_scores),
        'absconc_words_stdev':np.std(found_words_scores),
        'absconc_words_num':len(found_words),
        'absconc_words_str':found_words_str,        
    }


def _expand_str_by_psg(txt, psg_len=PSG_LEN):
    word2perc=get_absconc_wordscores_perc()
    bucket=[]
    got=0
    words_found = []
    sents = tokenize_sents_str(txt)
    for sent in sents: #get_tqdm(sents):
        for word in tokenize(sent):
            bucket.append(word)
            if word.lower() in word2perc: got+=1
        bucket.append(' ')
        if got>=psg_len and bucket:
            yield _get_psg_info(bucket)
            bucket=[]
            got=0
        bucket.append('\n|| ')
    if bucket: yield _get_psg_info(bucket)

def _expand_df_by_psg(df, df_key='psg_txt'):
    new = []
    for d in df.to_dict(orient='records'):
        for psg_d in _expand_str_by_psg(d[df_key]):
            new.append({
                **d,
                **psg_d,
                **{'psg_i':len(new)},
            })
    newdf=pd.DataFrame(new)
    return newdf.set_index('psg_i')


def score_absconc_psg(txt_or_df, key_df='psg_txt'):
    df = pd.DataFrame([{key_df:txt_or_df}]) if type(txt_or_df) is str else txt_or_df
    df = _expand_df_by_psg(df)
    return df
    