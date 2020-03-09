"""
Find out installation paths of PARI/GP
"""

#*****************************************************************************
#       Copyright (C) 2017 Jeroen Demeyer <jdemeyer@cage.ugent.be>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from __future__ import absolute_import, unicode_literals

import os, sys
from glob import glob

PARIDIR = None
for paridir in ('pari64', 'pari32', 'pari64u', 'pari32u', 'pari'):
    gphelp = os.path.join('libcache', paridir, 'bin', 'gphelp')
    if os.path.exists(gphelp):
        PARIDIR = paridir
        break
if not PARIDIR:
    raise RuntimeError('No gphelp found!')

prefix = os.path.join('libcache', PARIDIR)
gphelp = os.path.abspath(gphelp)
perl = os.path.join(r'C:\msys64', 'usr', 'bin', 'perl') if sys.platform == 'win32' else 'perl'

def pari_share():
    r"""
    Return the directory where the PARI data files are stored.

    EXAMPLES::

        >>> import os
        >>> from autogen.parser import pari_share
        >>> os.path.isfile(os.path.join(pari_share(), "pari.desc"))
        True
    """
    datadir = os.path.join(prefix, "share", "pari")
    if not os.path.isdir(datadir):
        raise EnvironmentError(
            "PARI data directory {!r} does not exist".format(datadir))
    return datadir

def include_dirs():
    """
    Return a list of directories containing PARI include files.
    """
    dirs = [os.path.join(prefix, "include")]
    return [d for d in dirs if os.path.isdir(os.path.join(d, "pari"))]


def library_dirs():
    """
    Return a list of directories containing PARI library files.
    """
    dirs = [os.path.join(prefix, s) for s in ("lib", "lib32", "lib64")]
    return [d for d in dirs if glob(os.path.join(d, "libpari*"))]
