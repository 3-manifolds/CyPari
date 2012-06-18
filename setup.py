from setuptools import setup, Command
from distutils.extension import Extension
from Cython.Distutils import build_ext

import os

pari_include_dir = ['.', 'pari-2.5.1/include']
pari_gen = Extension('cypari.gen',
                     sources = ['cypari/gen.pyx'],
                     include_dirs = pari_include_dir,
                     library_dirs = ['pari-2.5.1/lib'],
                     libraries = ['pari'])

class clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -f cypari/gen.c cypari/gen.h cypari/*.pyc')


setup(
  name = 'cypari',
  version = '1.0',
  packages = ['cypari'],
  cmdclass = {'build_ext': build_ext, 'clean':clean},
  ext_modules = [pari_gen],
  author = 'Marc Culler and Nathan Dunfield',
  author_email = 'culler@math.uic.edu, nmd@illinois.edu',
  description = "Sage's PARI extension, modified to stand alone.",
  license = 'GPL',
  keywords = 'Pari, Sage, SnapPy',
  url = 'http://www.math.uic.edu/t3m',
)
