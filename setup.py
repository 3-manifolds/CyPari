long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<https://github.com/sagemath/sage/blob/797dd7b4c273556d9677fadffa2ef6dd7f113857/src/sage/libs/cypari2/gen.pyx>`_
of `SageMath <http://www.sagemath.org>`_, but is independent of the rest of
SageMath and can be used with any recent version of Python 3.
"""

no_cython_message = """
Building CyPari requires Cython (>= 3.0.0) to be installed.
"""

import sys
if sys.version_info < (3,5):
    print("Python 3.6 or higher is required")
    sys.exit()
if not sys.maxsize > 2**32:
    raise RuntimeError('32 bit systems are no longer supported.')

import os
import re
import sysconfig
import subprocess
import shutil
import site
import platform
import time
from glob import glob
from setuptools import setup, Command
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist
from distutils.util import get_platform
from subprocess import Popen, PIPE

if sys.platform == 'win32':
    # We expect to be using:
    # * Windows Visual Studio 2022 with the Universal C Runtime and the
    #   Windows 11 SDK 10.0.22621.0 installed.
    # * An MSYS-2 with the UCRT64 environment installed for gcc
    #
    # For mysterious reasons, CyPari will not compile with the more
    # recent Windows 11 SDK 10.0.26000.0.  Setuptools will always use
    # the most recent version of the Windows 11 SDK, which is what MS
    # recommends since the result will still work on any earlier
    # version of Windows.  Therefore, we do a monkeypatch hack to
    # force the use of 10.0.22621.0 even if the newer version is
    # available.

    @staticmethod
    def _parse_path_hack(val):
        return [dir.rstrip(os.sep).replace('10.0.26100.0', '10.0.22621.0')
                for dir in val.split(os.pathsep) if dir]
    import distutils.compilers.C.msvc  # really setuptools._distutils.compilers.C.msvc
    distutils.compilers.C.msvc.Compiler._parse_path = _parse_path_hack


# Path setup for building with the mingw C compiler on Windows.
if sys.platform == 'win32' and not os.path.exists('libcache/pari'):
    # We always build the Pari library with mingw, no matter which compiler
    # is used for the CyPari extension.
    # Make sure that our C compiler matches our python and that we can run bash
    # and other needed utilities such as find.
    bash_proc = Popen(['bash', '-c', 'echo $PATH'], stdout=PIPE, stderr=PIPE)
    BASHPATH, _ = bash_proc.communicate()
    BASHPATH = BASHPATH.decode('utf8')
    BASH = r'C:\msys64\usr\bin\bash'
else:
    BASHPATH = os.environ['PATH']
    BASH = '/bin/bash'

PARIDIR = 'pari'
GMPDIR = 'gmp'
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
        junkfiles = (glob('cypari/*.so*') +
                     glob('cypari/*.pyc') +
                     glob('cypari/_pari.c') +
                     glob('cypari/_pari*.h') +
                     glob('cypari/auto*.pxi') +
                     glob('cypari/auto*.pxd') +
                     glob('cypari/*.tmp')
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
        version_info = sys.version_info
        if int(version_info[1]) < 11:
            build_lib_dir = os.path.join(
                'build',
                'lib.{platform}-{version_info[0]}.{version_info[1]}'.format(
                    platform=sysconfig.get_platform(),
                    version_info=sys.version_info)
                )
        else:
            build_lib_dir = os.path.join(
                'build',
                'lib.{platform}-cpython-{version_info[0]}{version_info[1]}'.format(
                    platform=sysconfig.get_platform(),
                    version_info=sys.version_info)
                )
        print(build_lib_dir)
        sys.path.insert(0, os.path.abspath(build_lib_dir))
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
    return (output + errors).decode().split()[1].split('.')[0]

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
        for filename in glob('cypari/_pari*.c'):
            os.remove(filename)

        pythons = os.environ.get('RELEASE_PYTHONS', sys.executable).split(',')
        print('releasing for: %s'%(', '.join(pythons)))
        for python in pythons:
            check_call([python, 'setup.py', 'clean'])
            check_call([python, 'setup.py', 'build'])
            check_call([python, 'setup.py', 'test'])
            # Save a copy of the _pari.c file for each major version of Python.
            _pari_c_name = '_pari_py%s.c'%python_major(python)
            _pari_c_path = os.path.join('cypari', _pari_c_name)
            if not os.path.exists(_pari_c_path):
                os.rename(os.path.join('cypari', '_pari.c'), _pari_c_path)
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
            building_sdist = True

        if (not os.path.exists(os.path.join('libcache', PARIDIR))
            or not os.path.exists(os.path.join('libcache', GMPDIR))):
            if sys.platform == 'win32':
                # This is meant to work even in a Windows Command Prompt
                cmd = r'export PATH="%s" ; export MSYSTEM=UCRT64 ; bash build_pari.sh'%BASHPATH
            else:
                cmd = r'export PATH="%s" ; bash build_pari.sh'%BASHPATH
            if subprocess.call([BASH, '-c', cmd]):
                sys.exit("***Failed to build PARI library***")

        if building_sdist:
            build_ext.run(self)
            return

        if (not os.path.exists(os.path.join('cypari', 'auto_gen.pxi')) or
            not os.path.exists(os.path.join('cypari', 'auto_instance.pxi'))):
            import autogen
            autogen.rebuild()

        # Provide declarations in an included .pxi file which indicate
        # whether we are building for 64 bit Python on Windows, and
        # which version of Python we are using.  We need to handle 64
        # bit Windows differently because (a) it is the only 64 bit
        # system with 32 bit longs and (b) Pari deals with this by:
        # #define long long long thereby breaking lots of stuff in the
        # Python headers.
        long_include = os.path.join('cypari', 'pari_long.pxi')
        if sys.platform == 'win32':
            if sys.version_info.major == 2:
                include_file = os.path.join('cypari', 'long_win64py2.pxi')
            else:
                include_file = os.path.join('cypari', 'long_win64py3.pxi')
        else:
            include_file = os.path.join('cypari', 'long_generic.pxi')
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
        # try:
        #     from Cython.Build import cythonize
        #     cythonize([os.path.join('cypari', '_pari.pyx')],
        #               compiler_directives={'language_level':2})
        # except ImportError:
        #     if not os.path.exists(os.path.join('cypari', '_pari.c')):
        #         sys.exit(no_cython_message)
        from Cython.Build import cythonize
        _pari_pyx = os.path.join('cypari', '_pari.pyx')
        _pari_c = os.path.join('cypari', '_pari.c')
        cythonize([_pari_pyx],
                  compiler_directives={'language_level':2})
        if sys.platform == 'win32':
            # patch _pari.c to deal with #define long long long
            with open('_pari.c', 'w') as outfile:
                with open(_pari_c) as infile:
                    for line in infile.readlines():
                        if (line.find('intrin.h') >= 0 or
                            line.find('pythread.h') >= 0):
                            outfile.write(
                                '  #undef long\n%s'
                                '  #define long long long\n' %line)
                        else:
                            outfile.write(line)
            os.unlink(_pari_c)
            os.rename('_pari.c', _pari_c)
        build_ext.run(self)

class CyPariSourceDist(sdist):

    def _tarball_info(self, lib):
        lib_re = re.compile(r'(%s-[0-9\.]+)\.tar\.[bg]z2*'%lib)
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
if sys.platform == 'darwin':
    compile_args=['-mmacosx-version-min=10.9', '-Wno-unreachable-code',
                      '-Wno-unreachable-code-fallthrough']
elif sys.platform == 'win32':
    # Ignore the assembly language inlines when building the extension.
    compile_args = ['/DDISABLE_INLINE']
    if False:  # Toggle for debugging symbols
        compile_args += ['/Zi']

    # libpari relies on a few mingw library functions not present in MSCV's default
    # libraries, so we need to add these:
    link_args += ['/alternatename:stat64i32=_stat64i32',
                  '/alternatename:___chkstk_ms=__chkstk',
                  '/alternatename:__mingw_sprintf=sprintf',
                  '/alternatename:__mingw_vsprintf=vsprintf',
                  'advapi32.lib',
                  'legacy_stdio_definitions.lib']
else:
    compile_args = []

link_args += [pari_static_library, gmp_static_library]
if sys.platform.startswith('linux'):
    link_args += ['-Wl,-Bsymbolic-functions', '-Wl,-Bsymbolic']

include_dirs = [pari_include_dir]

_pari = Extension(name='cypari._pari',
                  sources=['cypari/_pari.c'],
                  include_dirs=include_dirs,
                  extra_link_args=link_args,
                  extra_compile_args=compile_args)

# Load the version number.
sys.path.insert(0, 'cypari')
from version import __version__
sys.path.pop(0)

setup(
    name = 'cypari',
    version = __version__,
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari'],
    package_dir = {'cypari':'cypari'},
    cmdclass = {
        'build_ext': CyPariBuildExt,
        'clean': CyPariClean,
        'test': CyPariTest,
        'release': CyPariRelease,
        'sdist': CyPariSourceDist,
    },
    ext_modules = [_pari],
    zip_safe = False,
    long_description = long_description,
    url = 'https://bitbucket.org/t3m/cypari',
    author = 'Marc Culler and Nathan M. Dunfield',
    author_email = 'culler@uic.edu, nathan@dunfield.info',
    license = 'GPL-2.0-or-later',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    keywords = 'Pari, SageMath, SnapPy',
)
