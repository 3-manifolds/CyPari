long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<http://doc.sagemath.org/html/en/reference/libs/sage/libs/pari/index.html>`_
of `Sage <http://www.sagemath.org>`_, but is independent of the rest of
Sage and can be used with any recent version of Python.
"""

from setuptools import setup
import setuptools, setuptools.command.sdist, os, sys

# Static linking causes segfaults for some reason.
# So, to run Cypari you have to either *install* this version
# of Pari or set LD_LIBRARY_PATH.
# Either way, we build a local version of Pari in build/pari.
pari_include_dir = os.path.join('build', 'pari', 'include')
#pari_library_dir = os.path.join('build', 'pari')
pari_library_dir = '/usr/local/lib/'
#pari_library = os.path.join(pari_library_dir, 'libpari.a')

import cysignals
python_package_dir = os.path.dirname(os.path.dirname(cysignals.__file__))
cysignals_include_dir = os.path.join(python_package_dir, 'cysignals/')

if not os.path.exists('build/pari') and 'clean' not in sys.argv:
    if sys.platform == 'win32':
        print('Please run the bash script build_pari.sh first')
    if os.system('bash build_pari.sh') != 0:
        sys.exit("***Failed to build PARI library***")

if (not os.path.exists('cypari/auto_gen.pxi')
    or not os.path.exists('cypari/auto_instance.pxi')):
    import autogen
    autogen.autogen_all()

class clean(setuptools.Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -f cypari/gen.c cypari/pari_instance.c cypari/*.pyc')

try:
    from Cython.Build import cythonize
    if 'clean' not in sys.argv:
        cython_sources = ['cypari/gen.pyx',
                          'cypari/pari_instance.pyx',
                          'cypari/handle_error.pyx']
        cythonize(cython_sources, include_path=[python_package_dir])

except ImportError:
    pass 

pari_gen = setuptools.Extension('cypari.gen',
                     sources=['cypari/gen.c'],
                     include_dirs=[pari_include_dir, cysignals_include_dir],
                     library_dirs=[pari_library_dir],
                     libraries=['pari', 'm'],
                     )

pari_instance = setuptools.Extension('cypari.pari_instance',
                     sources=['cypari/pari_instance.c'],
                     include_dirs=[pari_include_dir, cysignals_include_dir],
                     library_dirs=[pari_library_dir],
                     libraries=['pari', 'm'],
                     )

pari_error = setuptools.Extension('cypari.handle_error',
                     sources=['cypari/handle_error.c'],
                     include_dirs=[pari_include_dir, cysignals_include_dir],
                     library_dirs=[pari_library_dir],
                     libraries=['pari'],
                     )

# Load version number
exec(open('cypari/version.py').read())

setup(
    name = 'cypari',
    version = version,
    install_requires = [],
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari'],
    package_dir = {'cypari':'cypari'}, 
    cmdclass = {'clean':clean},
    ext_modules = [pari_gen, pari_instance, pari_error],
    
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

