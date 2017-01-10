long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<http://doc.sagemath.org/html/en/reference/libs/sage/libs/pari/index.html>`_
of `Sage <http://www.sagemath.org>`_, but is independent of the rest of
Sage and can be used with any recent version of Python.
"""
import os, sys, sysconfig, subprocess, shutil

if sys.platform == 'win32':
    # Build with mingw by default.
    # msys2 should be installed in C:\msys64 for this
    if sys.argv[1:] == ['build']:
        sys.argv.append('-cmingw32')
    # make sure our C compiler matches our python and we can run bash
    if sys.maxsize > 2**32:
        # use mingw64
        WINPATH=r'C:\msys64\mingw64\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin'
        BASHPATH='/c/msys64/mingw64/bin:/c/msys64/usr/local/bin:/c/msys64/usr/bin'
    else:
        # use mingw32
        WINPATH=r'C:\msys64\mingw32\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin'
        BASHPATH='/c/msys64/mingw32/bin:/c/msys64/usr/local/bin:/c/msys64/usr/bin'
    os.environ['PATH'] = ';'.join([WINPATH, os.environ['PATH']])
    BASH = r'C:\msys64\usr\bin\bash'
else:
    BASHPATH = os.environ['PATH']
    BASH = '/bin/bash'

if sys.platform != 'darwin':
    if sys.maxsize > 2**32:
        PARIDIR = 'pari64'
    else:
        PARIDIR = 'pari32'
else:
    PARIDIR = 'pari'
    
from setuptools import setup, Command
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from Cython.Build import cythonize

# Load version number
exec(open('cypari_src/version.py').read())

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
        os.system('rm -rf build/lib* build/temp* build/bdist* dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -if cypari_src/*.pyc')
        os.system('rm -if cypari_src/*.so*')
        os.system('rm -if cypari_src/gen.c')
        os.system('rm -if cypari_src/gen_api.h')
        #os.system('rm -if cypari_src/auto*.pxi')

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
else:
    print('Command "release" is not supported for %s.'%sys.platform)

class CyPariRelease(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        for python in pythons:
            try:
                subprocess.check_call([python, 'setup.py', 'build'])
            except subprocess.CalledProcessError:
                print('Build failed for %s.'%python)
                sys.exit(1)
            try:
                subprocess.check_call([python, 'setup.py', 'test'])
            except subprocess.CalledProcessError:
                print('Test failed for %s.'%python)
                sys.exit(1)
            try:
                subprocess.check_call([python, 'setup.py', 'bdist_wheel'])
            except subprocess.CalledProcessError:
                print('Error building wheel for %s.'%python)
        print('Wheels are in the dist directory')

class CyPariBuildExt(build_ext):
    def __init__(self, dist):
        build_ext.__init__(self, dist)
        
    def run(self):
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

        if (not os.path.exists(os.path.join('cypari_src', 'auto_gen.pxi')) or
            not os.path.exists(os.path.join('cypari_src', 'auto_instance.pxi'))):
            import autogen
            autogen.autogen_all()
            
        # Provide compile time constants which indicate whether we
        # are building for 64 bit Python on Windows, and which version
        # of Python we are using.
        # We need to know about 64 bit Windows because it is the only 64 bit
        # system which we support that has 32 bit longs.
        # We have to work around the fact that Pari deals with this as:
        # #define long long long
        # thereby breaking lots of stuff.
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
    install_requires = ['future'],
    cmdclass = {
        'build_ext': CyPariBuildExt,
        'clean': CyPariClean,
        'test': CyPariTest,
        'release': CyPariRelease
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

