long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<http://doc.sagemath.org/html/en/reference/libs/sage/libs/pari/index.html>`_
of `Sage <http://www.sagemath.org>`_, but is independent of the rest of
Sage and can be used with any recent version of Python (except on Windows,
where 3.4 is currently the only supported version of Python 3).
"""
import os, sys, re, sysconfig, subprocess, shutil, site
from glob import glob
from setuptools import setup, Command
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist
from Cython.Build import cythonize

# Load the version number.
exec(open('cypari_src/version.py').read())

# Path setup for building with the mingw C compiler on Windows.
if sys.platform == 'win32':
    # Build with mingw by default.
    if sys.argv[1] == 'build':
        sys.argv.append('-cmingw32')
    # Make sure that our C compiler matches our python and that we can run bash
    # This assumes that msys2 is installed in C:\msys64.
    if sys.maxsize > 2**32:   # use mingw64
        WINPATH=r'C:\msys64\mingw64\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin'
        BASHPATH='/c/msys64/mingw64/bin:/c/msys64/usr/local/bin:/c/msys64/usr/bin'
    else:   # use mingw32
        WINPATH=r'C:\msys64\mingw32\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin'
        BASHPATH='/c/msys64/mingw32/bin:/c/msys64/usr/local/bin:/c/msys64/usr/bin'
    os.environ['PATH'] = ';'.join([WINPATH, os.environ['PATH']])
    BASH = r'C:\msys64\usr\bin\bash'
else:
    BASHPATH = os.environ['PATH']
    BASH = '/bin/bash'

# We build the 32 bit and 64 bit versions of the Pari library in separate
# directories, but in macOS we use lipo to combine them into a fat library.
if sys.platform != 'darwin':
    if sys.maxsize > 2**32:
        PARIDIR = 'pari64'
    else:
        PARIDIR = 'pari32'
else:
    PARIDIR = 'pari'
    
pari_include_dir = os.path.join('build', PARIDIR, 'include')
pari_library_dir = os.path.join('build', PARIDIR, 'lib')
pari_static_library = os.path.join(pari_library_dir, 'libpari.a')

class CyPariClean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        junkdirs = (glob('build/lib*') +
                    glob('build/bdist*') +
                    glob('cypari*.egg-info')
        )
        for dir in junkdirs:
            try:
                shutil.rmtree(dir)
            except OSError:
                pass
        junkfiles = (glob('cypari_src/*.so*') +
                     glob('cypari_src/*.pyc') +
                     ['cypari_src/gen.c', 'cypari_src/gen_api.h']
        )

class CyPariTest(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        build_lib_dir = os.path.join(
            'build',
            'lib.{platform}-{version_info[0]}.{version_info[1]}'.format(
                platform=sysconfig.get_platform(),
                version_info=sys.version_info)
        )
        sys.path.insert(0, build_lib_dir)
        from cypari.test import runtests
        sys.exit(runtests())

if sys.platform == 'win32':
    pythons = [
        r'C:\Python27\python.exe',
        r'C:\Python27-x64\python.exe',
        r'C:\Python34\python.exe',
        r'C:\Python34-x64\python.exe',
        ]
elif sys.platform == 'darwin':
    pythons = [
        'python2.7',
        'python3.4',
        'python3.5',
        'python3.6',
        ]
elif site.__file__.startswith('/opt/python/cp'):
    pythons = [
        'python2.7',
        'python3.4',
        'python3.5',
        'python3.6',
        ]
else:
    pythons = [
        'python2.7',
        'python3.5'
    ]

class CyPariRelease(Command):
    # The -rX option modifies the wheel name by adding rcX to the version string.
    # This is for uploading to testpypi, which will not allow uploading two
    # wheels with the same name.
    user_options = [('rctag=', 'r', 'index for rc tag to be appended to version (e.g. -r2 -> rc2)')]
    def initialize_options(self):
        self.rctag = None
    def finalize_options(self):
        if self.rctag:
            self.rctag = 'rc%s'%self.rctag
    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        for python in pythons:
            try:
                subprocess.check_call([python, 'setup.py', 'build'])
            except subprocess.CalledProcessError:
                raise RuntimeError('Build failed for %s.'%python)
                sys.exit(1)
            try:
                subprocess.check_call([python, 'setup.py', 'test'])
            except subprocess.CalledProcessError:
                raise RuntimeError('Test failed for %s.'%python)
                sys.exit(1)
            try:
                subprocess.check_call([python, 'setup.py', 'bdist_wheel'])
            except subprocess.CalledProcessError:
                raise RuntimeError('Error building wheel for %s.'%python)
        if sys.platform.startswith('linux'):
            # auditwheel generates names with more tags than allowed by pypi
            extra_tag = re.compile('linux_x86_64\.|linux_i686\.')
            # build wheels tagged as manylinux1
            for wheelname in [name for name in os.listdir('dist') if name.endswith('.whl')]:
                original_path = os.path.join('dist', wheelname)
                subprocess.check_call(['auditwheel', 'addtag', '-w', 'dist', original_path])
                os.remove(original_path)
        else:
            extra_tag = None
        version = re.compile('-([^-]*)-')
        for wheel_name in [name for name in os.listdir('dist') if name.endswith('.whl')]:
            new_name = wheel_name
            if extra_tag:
                new_name = extra_tag.sub('', new_name, 1)
            if self.rctag:
                new_name = version.sub('-\g<1>%s-'%self.rctag, new_name, 1)
            os.rename(os.path.join('dist', wheel_name), os.path.join('dist', new_name))
        try:
            subprocess.check_call(['python', 'setup.py', 'sdist'])
        except subprocess.CalledProcessError:
            raise RuntimeError('Error building sdist archive for %s.'%python)
        sdist_version = re.compile('-([^-]*)(.tar.gz)|-([^-]*)(.zip)')
        for archive_name in [name for name in os.listdir('dist')
                             if name.endswith('tar.gz') or name.endswith('.zip')]:
            if self.rctag:
                new_name = sdist_version.sub('-\g<1>%s\g<2>'%self.rctag, archive_name, 1)
                os.rename(os.path.join('dist', archive_name), os.path.join('dist', new_name))

class CyPariBuildExt(build_ext):
        
    def run(self):
        building_sdist = False
        
        if os.path.exists('pari_src'):
            # We are building an sdist.  Move the Pari source code into build.
            if not os.path.exists('build'):
                os.mkdir('build')
            os.rename('pari_src', os.path.join('build', 'pari_src'))
            building_sdist = True
        
        if not os.path.exists(os.path.join('build', PARIDIR)):
            # This is meant to work even  in a Windows Command Prompt
            if sys.platform == 'win32':
                cmd = r'export PATH="%s" ; export MSYSTEM=MINGW32 ; bash build_pari.sh %s'%(BASHPATH, PARIDIR)
            elif sys.platform == 'darwin':
                cmd = r'export PATH="%s" ; bash build_pari.sh'%BASHPATH
            else:
                cmd = r'export PATH="%s" ; bash build_pari.sh %s'%(BASHPATH, PARIDIR)
            print([BASH, '-c', cmd])
            if subprocess.call([BASH, '-c', cmd]):
                sys.exit("***Failed to build PARI library***")

        if building_sdist:
            build_ext.run(self)
            return

        if (not os.path.exists(os.path.join('cypari_src', 'auto_gen.pxi')) or
            not os.path.exists(os.path.join('cypari_src', 'auto_instance.pxi'))):
            import autogen
            autogen.autogen_all()
            
        # Provide compile time constants which indicate whether we are
        # building for 64 bit Python on Windows, and which version of
        # Python we are using.  We need to handle 64 bit Windows
        # differently because (a) it is the only 64 bit system with 32
        # bit longs and (b) Pari deals with this by:
        #  #define long long long
        # thereby breaking lots of stuff in the Python headers.
        ct_filename = os.path.join('cypari_src', 'ct_constants.pxi') 
        ct_constants = b''
        if sys.platform == 'win32' and sys.maxsize > 2**32:
            ct_constants += b'DEF WIN64 = True\n'
        else:
            ct_constants += b'DEF WIN64 = False\n'
        ct_constants += ('DEF PYTHON_MAJOR = %d\n'%sys.version_info.major).encode('ascii')
        if os.path.exists(ct_filename):
            with open(ct_filename) as input:
                old_constants = input.read().encode('ascii')
        else:
            old_constants = ''
        if old_constants != ct_constants:
            with open(ct_filename, 'wb') as output:
                output.write(ct_constants)
                
        cythonize([os.path.join('cypari_src', 'gen.pyx')])
        build_ext.run(self)

class CyPariSourceDist(sdist):
        
    def run(self):
        os.rename(os.path.join('build', 'pari_src'), 'pari_src')
        sdist.run(self)
        os.rename('pari_src', os.path.join('build', 'pari_src'))

link_args = []
compile_args = []
if sys.platform == 'win32':
    if sys.version_info.major == 3:
        link_args = ['-specs=specs100']
    else:
        link_args = ['-specs=specs90']
    link_args += ['-Wl,--subsystem,windows']
    compile_args += ['-D__USE_MINGW_ANSI_STDIO',
                     '-Dprintf=__MINGW_PRINTF_FORMAT']
    if sys.maxsize > 2**32:
        compile_args.append('-DMS_WIN64')
link_args += [pari_static_library]

include_dirs = []
include_dirs=[pari_include_dir]
pari_gen = Extension('cypari.gen',
                     sources=['cypari_src/gen.c'],
                     include_dirs=include_dirs,
                     extra_link_args=link_args,
                     extra_compile_args=compile_args)

setup(
    name = 'cypari',
    version = version,
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari'],
    package_dir = {'cypari':'cypari_src'},
    install_requires = ['six', 'future'],
    cmdclass = {
        'build_ext': CyPariBuildExt,
        'clean': CyPariClean,
        'test': CyPariTest,
        'release': CyPariRelease,
        'sdist': CyPariSourceDist,
    },
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

