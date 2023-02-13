from .imports import *

@click.group()
def cli(): pass

@cli.command()
@click.argument('what', type=click.Choice(['sents','tokens','types']))
@click.option('--num_proc', default=1)
@click.option('--lim', default=0)
def embed(what, num_proc=1, lim=0):
    """Embed things"""
    click.echo(f'Embedding {what}...')
    if what=='sents':
        embed_sents(num_proc=num_proc, lim=lim if lim else None)
    elif what=='tokens':
        embed_tokens(num_proc=num_proc, lim=lim if lim else None)

@cli.command()
def shell():
    """Enter interactive shell"""
    click.echo(f'Entering ipython')
    pyexec = 'ipython' if shutil.which('ipython') else 'python'
    imps='from contxt import *'
    opens=f'\nIn [0]: {imps}'
    return os.system(f'{pyexec} -i -c "{imps}"')



@cli.command()
@click.argument('corpus', type=click.Choice(['chadwyck','ppa']))
@click.option('--num_proc', default=1)
@click.option('--lim', default=0)
def compile(corpus, num_proc=1, lim=0):
    """Compile corpora"""
    click.echo(f'Compiling {corpus}...')
    if corpus=='ppa':
        PPACorpus().compile(num_proc=num_proc,lim=lim if lim else None)
    elif corpus=='chadwyck':
        ChadwyckCorpus().compile(num_proc=num_proc,lim=lim if lim else None)
