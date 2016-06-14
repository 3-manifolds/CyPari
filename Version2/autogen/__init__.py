import os

def autogen_all():
    """
    Regenerate the automatically generated files of the Sage library.
    """
    import pari
    pari.rebuild()
