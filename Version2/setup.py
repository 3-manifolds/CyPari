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

pari_include_dir = os.path.join('build', 'pari', 'include')
pari_library_dir = os.path.join('build', 'pari', 'lib')
pari_static_library = os.path.join(pari_library_dir, 'libpari.a')

if not os.path.exists('build/pari') and 'clean' not in sys.argv:
    if sys.platform == 'win32':
        print('Please run the bash script build_pari.sh first')
    if os.system('bash build_pari.sh') != 0:
        sys.exit("***Failed to build PARI library***")

if (not os.path.exists('cypari/auto_gen.pxi')
    or not os.path.exists('cypari/auto_instance.pxi')):
    import autogen
    autogen.autogen_all()

class Clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build/lib* build/temp* build/bdist* dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -if cypari/*.c')
        os.system('rm -if cypari/*.pyc')
        os.system('rm -if cypari/*.so*')

class CyPariBuildExt(build_ext):
    def __init__(self, dist):
        build_ext.__init__(self, dist)
        
    def run(self):
        build_ext.run(self)

include_dirs = []
if 'clean' not in sys.argv:
    try:
        import cysignals
    except ImportError:
        print 'Please install cysignals before building CyPari: "pip install cysignals".'
        sys.exit()
    python_package_dir = os.path.dirname(os.path.dirname(cysignals.__file__))
    cysignals_include_dir = os.path.join(python_package_dir, 'cysignals/')
    include_dirs=[pari_include_dir, cysignals_include_dir]
    cython_sources = ['cypari/gen.pyx']
    cythonize(cython_sources, include_path=[python_package_dir])

pari_gen = Extension('cypari.gen',
                     sources=['cypari/gen.c'],
                     include_dirs=include_dirs,
                     extra_link_args=[pari_static_library],
)

# Load version number
exec(open('cypari/version.py').read())

setup(
    name = 'cypari',
    version = version,
    install_requires = ['cysignals'],
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari'],
    package_dir = {'cypari':'cypari'},
    cmdclass = {'clean':Clean, 'build_ext':CyPariBuildExt},
    ext_modules = [pari_gen],
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

