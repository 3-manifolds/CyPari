long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<http://doc.sagemath.org/html/en/reference/libs/sage/libs/pari/index.html>`_
of `Sage <http://www.sagemath.org>`_, but is independent of the rest of
Sage and can be used with any recent version of Python.
"""

from setuptools import setup, Command
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from Cython.Build import cythonize
import os, sys

compiler_name = None
for arg in sys.argv:
    if arg.startswith('--compiler='):
        compiler_name = arg.split('=')[1]

pari_include_dir = 'build/pari/include'
pari_library_dir = 'build/pari/lib'
pari_static_library = os.path.join(pari_library_dir, 'libpari.a')
    
class Clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build/lib* build/temp* build/bdist* dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -if cypari_src/*.pyc')
        os.system('rm -if cypari_src/*.so*')
        os.system('rm -if cypari_src/gen.c')
        os.system('rm -if cypari_src/gen_api.h')
        
class CyPariBuildExt(build_ext):
    def __init__(self, dist):
        build_ext.__init__(self, dist)
        
    def run(self):
        build_ext.run(self)

if not os.path.exists('build/pari') and 'clean' not in sys.argv:
    if os.system('bash build_pari.sh') != 0:
        sys.exit("***Failed to build PARI library***")

if (not os.path.exists('cypari_src/auto_gen.pxi')
    or not os.path.exists('cypari_src/auto_instance.pxi')):
    if 'clean' not in sys.argv:
        import autogen
        autogen.autogen_all()

include_dirs = []
if 'clean' not in sys.argv:
    include_dirs=[pari_include_dir]
    cython_sources = ['cypari_src/gen.pyx']
    cythonize(cython_sources)

spec = ['-specs=specs90'] if sys.platform == 'win32' else []
    
pari_gen = Extension('cypari.gen',
                     sources=['cypari_src/gen.c'],
                     include_dirs=include_dirs,
                     extra_link_args=[pari_static_library] + spec,
)

# Load version number
exec(open('cypari_src/version.py').read())

cypari_extensions = [pari_gen]

setup(
    name = 'cypari',
    version = version,
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari'],
    package_dir = {'cypari':'cypari_src'},
    cmdclass = {'clean':Clean, 'build_ext':CyPariBuildExt},
    ext_modules = cypari_extensions,
    zip_safe = False,
    long_description = long_description,
    url = 'https://bitbucket.org/t3m/cypari',
    author = 'Marc Culler and Nathan M. Dunfield',
    author_email = 'culler@uic.edu, nathan@dunfield.info',
    license='GPLv2+',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    keywords = 'Pari, Sage, SnapPy',
)

