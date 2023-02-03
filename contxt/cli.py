from .imports import *

@click.group()
def cli(): pass

@cli.command()
@click.argument('what', type=click.Choice(['sents','words']))
@click.option('--num_proc', default=1)
@click.option('--lim', default=0)
def embed(what, num_proc=1, lim=0):
    """Embed things"""
    click.echo(f'Embedding {what}...')
    if what=='sents':
        embed_sents(num_proc=num_proc, lim=lim if lim else None)

@cli.command()
def shell():
    """Enter interactive shell"""
    click.echo(f'Entering ipython')
    pyexec = 'ipython' if shutil.which('ipython') else 'python'
    imps='from contxt import *'
    opens=f'\nIn [0]: {imps}'
    return os.system(f'{pyexec} -i -c "{imps}"')