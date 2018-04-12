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
from subprocess import Popen, PIPE

cpu_width = '64bit' if sys.maxsize > 2**32 else '32bit'

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
    # and other needed utilities such as find.
    bash_proc = Popen(['bash', '-c', 'echo $PATH'], stdout=PIPE, stderr=PIPE)
    BASHPATH, _ = bash_proc.communicate()
    BASHPATH = BASHPATH.decode('utf8')
    if cpu_width == '64bit':   # use mingw64
        TOOLCHAIN_W = r'C:\mingw-w64\x86_64-6.3.0-posix-seh-rt_v5-rev1\mingw64'
        TOOLCHAIN_U = '/c/mingw-w64/x86_64-6.3.0-posix-seh-rt_v5-rev1/mingw64'
        WINPATH=r'%s\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin;'%TOOLCHAIN_W
        BASHPATH='%s/bin:/c/msys64/usr/bin:'%TOOLCHAIN_U + BASHPATH
    else:   # use mingw32
        TOOLCHAIN_W = r'C:\mingw-w64\i686-6.3.0-posix-dwarf-rt_v5-rev1\mingw32'
        TOOLCHAIN_U = '/c/mingw-w64/i686-6.3.0-posix-dwarf-rt_v5-rev1/mingw32'
        WINPATH=r'%s\bin;C:\msys64\usr\local\bin;C:\msys64\usr\bin;'%TOOLCHAIN_W
        BASHPATH='%s/bin:/c/msys64/usr/bin:'%TOOLCHAIN_U + BASHPATH
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
    GMPDIR = 'gmp'
elif sys.platform == 'win32':
    if cpu_width == '64bit':
        if sys.version_info >= (3,5):
            PARIDIR = 'pari64u'
            GMPDIR = 'gmp64u'
        else:
            PARIDIR = 'pari64'
            GMPDIR = 'gmp64'
    else:
        if sys.version_info >= (3,5):
            PARIDIR = 'pari32u'
            GMPDIR = 'gmp32u'
        else:
            PARIDIR = 'pari32'
            GMPDIR = 'gmp32'
else:
    if cpu_width  == '64bit':
        GMPDIR = 'gmp64'
        PARIDIR = 'pari64'
    else:
        GMPDIR = 'gmp32'
        PARIDIR = 'pari32'
    
pari_include_dir = os.path.join('libcache', PARIDIR, 'include')
pari_library_dir = os.path.join('libcache', PARIDIR, 'lib')
pari_static_library = os.path.join(pari_library_dir, 'libpari.a')
gmp_library_dir = os.path.join('libcache', GMPDIR, 'lib')
gmp_static_library = os.path.join(gmp_library_dir, 'libgmp.a')

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
                     glob('cypari_src/_pari.c') +
                     glob('cypari_src/_pari*.h') +
                     glob('cypari_src/auto*.pxi')
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
        for filename in glob('cypari_src/_pari*.c'):
            os.remove(filename)

        pythons = os.environ.get('RELEASE_PYTHONS', sys.executable).split(',')
        print('releasing for: %s'%(', '.join(pythons)))
        for python in pythons:
            check_call([python, 'setup.py', 'clean'])
            check_call([python, 'setup.py', 'build'])
            check_call([python, 'setup.py', 'test'])
            # Save a copy of the _pari.c file for each major version of Python.
            _pari_c_name = '_pari_py%s.c'%python_major(python)
            _pari_c_path = os.path.join('cypari_src', _pari_c_name)
            if not os.path.exists(_pari_c_path):
                os.rename(os.path.join('cypari_src', '_pari.c'), _pari_c_path)
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

win64_py3_decls = b'''
'''

win64_py2_decls = b'''
'''

decls = b'''
'''

class CyPariBuildExt(build_ext):
        
    def run(self):
        building_sdist = False
        
        if os.path.exists('pari_src'):
            # We are building an sdist.  Move the Pari source code into build.
            if not os.path.exists('build'):
                os.mkdir('build')
            os.rename('pari_src', os.path.join('build', 'pari_src'))
            os.rename('gmp_src', os.path.join('build', 'gmp_src'))
            # Find the correct _pari.c for our version of Python.
            _pari_c_name = '_pari_py%d.c'%sys.version_info.major
            os.rename(os.path.join('cypari_src', _pari_c_name),
                      os.path.join('cypari_src', '_pari.c'))
            building_sdist = True
        
        if (not os.path.exists(os.path.join('libcache', PARIDIR))
            or not os.path.exists(os.path.join('libcache', GMPDIR))):
            if sys.platform == 'win32':
                # This is meant to work even in a Windows Command Prompt
                cmd = r'export PATH="%s" ; export MSYSTEM=MINGW32 ; bash build_pari.sh %s %s'%(BASHPATH, PARIDIR, GMPDIR)
            elif sys.platform == 'darwin':
                cmd = r'export PATH="%s" ; bash build_pari.sh'%BASHPATH
            else:
                cmd = r'export PATH="%s" ; bash build_pari.sh %s %s'%(BASHPATH, PARIDIR, GMPDIR)
            # print([BASH, '-c', cmd])
            if subprocess.call([BASH, '-c', cmd]):
                sys.exit("***Failed to build PARI library***")

        if building_sdist:
            build_ext.run(self)
            return

        if (not os.path.exists(os.path.join('cypari_src', 'auto_gen.pxi')) or
            not os.path.exists(os.path.join('cypari_src', 'auto_instance.pxi'))):
            import autogen
            autogen.autogen_all()
            
        # Provide declarations in an included .pxi file which indicate
        # whether we are building for 64 bit Python on Windows, and
        # which version of Python we are using.  We need to handle 64
        # bit Windows differently because (a) it is the only 64 bit
        # system with 32 bit longs and (b) Pari deals with this by:
        # #define long long long thereby breaking lots of stuff in the
        # Python headers.
        long_include = os.path.join('cypari_src', 'pari_long.pxi')
        if sys.platform == 'win32' and cpu_width == '64bit':
            if sys.version_info.major == 2:
                include_file = os.path.join('cypari_src', 'long_win64py2.pxi')
            else:
                include_file = os.path.join('cypari_src', 'long_win64py3.pxi')
        else:
            include_file = os.path.join('cypari_src', 'long_generic.pxi')
        with open(include_file, 'rb') as input:
            code = input.read()
        # Don't touch the long_include file unless it has changed, to avoid
        # unnecessary compilation.
        if os.path.exists(long_include):
            with open(long_include, 'rb') as input:
                old_code = input.read()
        else:
            old_code = b''
        if old_code != code:
            with open(long_include, 'wb') as output:
                output.write(code)

        # If we have Cython, check that .c files are up to date
        try: 
            from Cython.Build import cythonize
            cythonize([os.path.join('cypari_src', '_pari.pyx')])
        except ImportError:
            if not os.path.exists(os.path.join('cypari_src', '_pari.c')):
                sys.exit("***Cython needed to create cypari_src/_pari.c***")

        build_ext.run(self)

class CyPariSourceDist(sdist):
    
    def _tarball_info(self, lib):
        lib_re = re.compile('(%s-[0-9\.]+)\.tar\.[bg]z2*'%lib)
        for f in os.listdir('.'):
            lib_match = lib_re.search(f)
            if lib_match:
                break
        return lib_match.group(), lib_match.groups()[0]
    
    def run(self):
        tarball, dir = self._tarball_info('pari')
        check_call(['tar', 'xfz', tarball])
        os.rename(dir, 'pari_src')
        tarball, dir = self._tarball_info('gmp')
        check_call(['tar', 'xfj', tarball])
        os.rename(dir, 'gmp_src')
        sdist.run(self)
        shutil.rmtree('pari_src')
        shutil.rmtree('gmp_src')

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
    if False:  # Toggle for debugging symbols
        compile_args += ['/Zi']
        link_args += ['/DEBUG']
    # Add the mingw crt objects needed by libpari.
    if cpu_width == '64bit':
        link_args += [os.path.join('Windows', 'crt', 'libparicrt64.a'),
                      'advapi32.lib']
        if sys.version_info >= (3, 5):
            link_args += [
                'legacy_stdio_definitions.lib',
                os.path.join('Windows', 'crt', 'get_output_format64.o')]
    else:
        link_args += [os.path.join('Windows', 'crt', 'libparicrt32.a'),
                      'advapi32.lib']
        if sys.version_info >= (3, 5):
            link_args += [
                'legacy_stdio_definitions.lib', 'advapi32.lib',
                os.path.join('Windows', 'crt', 'get_output_format32.o')]

link_args += [pari_static_library, gmp_static_library]
    
if sys.platform.startswith('linux'):
    link_args += ['-Wl,-Bsymbolic-functions', '-Wl,-Bsymbolic']

include_dirs = []
include_dirs=[pari_include_dir]
pari_gen = Extension('cypari._pari',
                     sources=['cypari_src/_pari.c'],
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

