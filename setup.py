from setuptools import setup
import setuptools, setuptools.command.sdist, os, sys

pari_ver = 'pari-2.5.5'
pari_include_dir = os.path.join(pari_ver, 'include')
pari_library_dir = os.path.join(pari_ver, 'lib')
pari_library = os.path.join(pari_library_dir, 'libpari.a')

if not os.path.exists(pari_library) and 'clean' not in sys.argv:
    if sys.platform == 'win32':
        print 'Please run the bash script build_pari.sh first'
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

class sdist(setuptools.command.sdist.sdist):
    def run(self):
        from Cython.Build import cythonize
        cythonize(['cypari_src/gen.pyx'])
        setuptools.command.sdist.sdist.run(self)
        

cmdclass = {'clean':clean, 'sdist':sdist}

try:
    from Cython.Distutils import build_ext
    have_cython, source_ext = True, '.pyx'
    cmdclass['build_ext'] = build_ext
except ImportError:
    have_cython, source_ext = False, '.c'
    

pari_gen = setuptools.Extension('cypari_src.gen',
                     sources=['cypari_src/gen' + source_ext],
                     include_dirs=['cypari_src', pari_include_dir],
                     library_dirs=[pari_library_dir],
                     libraries=['pari', 'm'],
                     )

setup(
  name = 'cypari',
  version = '1.2',
  zip_safe = False,
  packages = ['cypari'],
  package_dir = {'cypari':'cypari_src'}, 
  cmdclass = cmdclass,
  ext_modules = [pari_gen],
  author = 'Marc Culler and Nathan Dunfield',
  author_email = 'culler@math.uic.edu, nmd@illinois.edu',
  description = "Sage's PARI extension, modified to stand alone.",
  license = 'GPL v2+',
  keywords = 'Pari, Sage, SnapPy',
  url = 'http://www.math.uic.edu/t3m',
)

