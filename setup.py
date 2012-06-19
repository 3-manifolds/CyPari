from setuptools import setup, Command
from distutils.extension import Extension
from Cython.Distutils import build_ext

import os, sys
pari_ver = 'pari-2.5.1'
pari_include_dir = os.path.join(pari_ver, 'include')
pari_library_dir = os.path.join(pari_ver, 'lib')
pari_library = os.path.join(pari_library_dir, 'libpari.a')
command = sys.argv[1]
print "HI THERE: " + command

if ( command in ['build', 'build_ext', 'install', 'bdist_egg'] and
     not os.path.exists(pari_library) ):
    os.system('sh build_pari.sh')
    
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

pari_gen = Extension('cypari.gen',
                     sources = ['cypari/gen.pyx'],
                     include_dirs = [pari_include_dir],
                     library_dirs = [pari_library_dir],
                     libraries = ['pari'])

setup(
  name = 'cypari',
  version = '1.0',
  zip_safe = False,
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
