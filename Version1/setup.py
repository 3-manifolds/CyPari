long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<http://www.sagemath.org/doc/reference/libs/sage/libs/pari/gen.html>`_
of `Sage <http://www.sagemath.org>`_, but is independent of the rest of
Sage and can be used with any recent version of Python.
"""


from setuptools import setup
import setuptools, setuptools.command.sdist, os, sys

pari_ver = 'pari-2.5.5'
pari_include_dir = os.path.join(pari_ver, 'include')
pari_library_dir = os.path.join(pari_ver, 'lib')
pari_library = os.path.join(pari_library_dir, 'libpari.a')

if not os.path.exists(pari_library) and 'clean' not in sys.argv:
    if sys.platform == 'win32':
        print('Please run the bash script build_pari.sh first')
        sys.exit()
    if os.system('bash build_pari.sh') != 0:
        sys.exit("***Failed to build PARI library***")
    
class clean(setuptools.Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -f cypari_src/gen.c cypari_src/gen.h cypari_src/*.pyc')

try:
    from Cython.Build import cythonize
    if 'clean' not in sys.argv:
        target = 'cypari_src/gen.pyx'
        if os.path.exists(target):
            cythonize([target])

except ImportError:
    pass 

if sys.platform == 'win32':
    extra_link_args = ['-static-libgcc', '-specs=specs90']
else:
    extra_link_args = []

pari_gen = setuptools.Extension('cypari.gen',
                     sources=['cypari_src/gen.c'],
                     include_dirs=[pari_include_dir],
                     library_dirs=[pari_library_dir],
                     libraries=['pari', 'm'],
                     extra_link_args=extra_link_args
                     )

# Load version number
exec(open('cypari_src/version.py').read())

setup(
    name = 'cypari',
    version = version,
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari'],
    package_dir = {'cypari':'cypari_src'}, 
    cmdclass = {'clean':clean},
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

