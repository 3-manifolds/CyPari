import os

PARIDIR = None
for paridir in ('pari64', 'pari32', 'pari64u', 'pari32u', 'pari'):
    gphelp = os.path.join('build', paridir, 'bin', 'gphelp')
    if os.path.exists(gphelp):
        PARIDIR = paridir
        break
if not PARIDIR:
    raise RuntimeError('No gphelp found!')

def autogen_all():
    """
    Regenerate the automatically generated files of the Sage library.
    """
    from . import pari
    pari.rebuild()
