long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<https://github.com/sagemath/sage/blob/797dd7b4c273556d9677fadffa2ef6dd7f113857/src/sage/libs/cypari2/gen.pyx>`_
of `SageMath <http://www.sagemath.org>`_, but is independent of the rest of
SageMath and can be used with any recent version of Python 2 or 3.
"""
import os, sys, re, sysconfig, subprocess, shutil, site, platform, time
from glob import glob
from setuptools import setup, Command
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist
from distutils.util import get_platform

cpu_width = platform.architecture()[0]

if sys.platform == 'win32':
    compiler_set = False
    ext_compiler = 'msvc'
    for n, arg in enumerate(sys.argv):
        if arg == '-c':
            ext_compiler = sys.argv[n+1]
            compiler_set = True
            break
        elif arg.startswith('-c'):
            ext_compiler = arg[2:]
            compiler_set = True
            break
        elif arg.startswith('--compiler'):
            ext_compiler = arg.split('=')[1]
            compiler_set = True
            break
    if not compiler_set and 'build' in sys.argv:
        sys.argv.append('--compiler=msvc')
else:
    ext_compiler = ''

# Path setup for building with the mingw C compiler on Windows.
if sys.platform == 'win32':
    # We always build the Pari library with mingw, no matter which compiler
    # is used for the CyPari extension.
    # Make sure that our C compiler matches our python and that we can run bash
    # This assumes that msys2 is installed in C:\msys64.
    if cpu_width == '64bit':   # use mingw64
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
# On Windows we also build separately for the Universal CRT on Python >= 3.5
if sys.platform == 'darwin':
    PARIDIR = 'pari'
elif sys.platform == 'win32':
    if cpu_width == '64bit':
        if sys.version_info >= (3,5):
            PARIDIR = 'pari64u'
        else:
            PARIDIR = 'pari64'
    else:
        if sys.version_info >= (3,5):
            PARIDIR = 'pari32u'
        else:
            PARIDIR = 'pari32'
else:
    if cpu_width  == '64bit':
        PARIDIR = 'pari64'
    else:
        PARIDIR = 'pari32'
    
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
                    glob('build/temp*') +
                    glob('cypari*.egg-info')
        )
        for dir in junkdirs:
            try:
                shutil.rmtree(dir)
            except OSError:
                pass
        junkfiles = (glob('cypari_src/*.so*') +
                     glob('cypari_src/*.pyc') +
                     glob('cypari_src/gen.c') +
                     glob('cypari_src/gen*.h')
        )
        for file in junkfiles:
            try:
                os.remove(file)
            except OSError:
                pass

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

def check_call(args):
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError:
        executable = args[0]
        command = [a for a in args if not a.startswith('-')][-1]
        raise RuntimeError(command + ' failed for ' + executable)

def python_major(python):
    proc = subprocess.Popen([python, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = proc.communicate()
    # Python 2 writes to stderr, but Python 3 writes to stdout
    return (output + errors).split()[1].split('.')[0]
    
class CyPariRelease(Command):
    user_options = [('install', 'i', 'install the release into each Python')]
    def initialize_options(self):
        self.install = False
    def finalize_options(self):
        pass
    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        for filename in glob('cypari_src/gen*.c'):
            os.remove(filename)

        pythons = os.environ.get('RELEASE_PYTHONS', sys.executable).split(',')
        print('releasing for: %s'%(', '.join(pythons)))
        for python in pythons:
            check_call([python, 'setup.py', 'clean'])
            check_call([python, 'setup.py', 'build'])
            check_call([python, 'setup.py', 'test'])
            # Save a copy of the gen.c file for each major version of Python.
            gen_c_name = 'gen_py%s.c'%python_major(python)
            gen_c_path = os.path.join('cypari_src', gen_c_name)
            if not os.path.exists(gen_c_path):
                os.rename(os.path.join('cypari_src', 'gen.c'), gen_c_path)
            if sys.platform.startswith('linux'):
                plat = get_platform().replace('linux', 'manylinux1')
                plat = plat.replace('-', '_')
                check_call([python, 'setup.py', 'bdist_wheel', '-p', plat])
                check_call([python, 'setup.py', 'bdist_egg'])
            else:
                check_call([python, 'setup.py', 'bdist_wheel'])

            if self.install:
                check_call([python, 'setup.py', 'install'])

        # Build sdist using the *first* specified Python
        check_call([pythons[0], 'setup.py', 'sdist'])

        # Double-check the Linux wheels
        if sys.platform.startswith('linux'):
            for name in os.listdir('dist'):
                if name.endswith('.whl'):
                    subprocess.check_call(['auditwheel', 'repair',
                                           os.path.join('dist', name)])

class CyPariBuildExt(build_ext):
        
    def run(self):
        building_sdist = False
        
        if os.path.exists('pari_src'):
            # We are building an sdist.  Move the Pari source code into build.
            if not os.path.exists('build'):
                os.mkdir('build')
            os.rename('pari_src', os.path.join('build', 'pari_src'))
            # Find the correct gen.c for our version of Python.
            gen_c_name = 'gen_py%d.c'%sys.version_info.major
            os.rename(os.path.join('cypari_src', gen_c_name),
                      os.path.join('cypari_src', 'gen.c'))
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
        if sys.platform == 'win32' and cpu_width == '64bit':
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

        # If have Cython, check that .c files are up to date
        try: 
            from Cython.Build import cythonize
            cythonize([os.path.join('cypari_src', 'gen.pyx')])
        except ImportError:
            if not os.path.exists(os.path.join('cypari_src', 'gen.c')):
                sys.exit("***Cython needed to create cypari_src/gen.c***")

        build_ext.run(self)

class CyPariSourceDist(sdist):
        
    def run(self):
        os.rename(os.path.join('build', 'pari_src'), 'pari_src')
        sdist.run(self)
        os.rename('pari_src', os.path.join('build', 'pari_src'))

link_args = []
compile_args = []
if ext_compiler == 'mingw32':
    major, minor = sys.version_info.major, sys.version_info.minor
    if major == 3:
        if minor == 4:
            link_args = [r'C:\Windows\System32\Python34.dll']
        link_args += ['-specs=specs100']
    else:
        link_args = ['-specs=specs90']
    link_args += ['-Wl,--subsystem,windows']
    compile_args += ['-D__USE_MINGW_ANSI_STDIO',
                     '-Dprintf=__MINGW_PRINTF_FORMAT']
    if cpu_width == '64bit':
        compile_args.append('-DMS_WIN64')
elif ext_compiler == 'msvc':
    # Ignore the assembly language inlines when building the extension.
    compile_args += ['/DDISABLE_INLINE']
    # Add the mingw crt objects needed by libpari.
    if cpu_width == '64bit':
        link_args += [os.path.join('Windows', 'crt', 'libparicrt64.a')]
        if sys.version_info >= (3, 5):
            link_args += [os.path.join('Windows', 'crt', 'get_output_format64.o')]
    else:
        link_args += [os.path.join('Windows', 'crt', 'libparicrt32.a')]
        if sys.version_info >= (3, 5):
            link_args += [os.path.join('Windows', 'crt', 'get_output_format32.o')]
link_args += [pari_static_library]
    
if sys.platform.startswith('linux'):
    link_args += ['-Wl,-Bsymbolic-functions', '-Wl,-Bsymbolic']

include_dirs = []
include_dirs=[pari_include_dir]
pari_gen = Extension('cypari.gen',
                     sources=['cypari_src/gen.c'],
                     include_dirs=include_dirs,
                     extra_link_args=link_args,
                     extra_compile_args=compile_args)

# Load the version number.
sys.path.insert(0, 'cypari_src')
from version import __version__
sys.path.pop(0)

setup(
    name = 'cypari',
    version = __version__,
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
    keywords = 'Pari, SageMath, SnapPy',
)

