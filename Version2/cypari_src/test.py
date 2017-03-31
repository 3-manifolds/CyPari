from __future__ import print_function
import doctest, re, getopt, sys
from . import tests
from . import _pari
from ._pari import Pari
import sys
if sys.version_info.major == 2:
    from . import py2tests
else:
    from . import py3tests

cpu_width = '64bit' if sys.maxsize > 2**32 else '32bit'

class DocTestParser(doctest.DocTestParser):

    def parse(self, string, name='<string>'):
        # Remove tests for the wrong architecture
        regex32 = re.compile(r'(\n.*?)\s+# 32-bit\s*$', re.MULTILINE)
        regex64 = re.compile(r'(\n.*?)\s+# 64-bit\s*$', re.MULTILINE)
        if cpu_width == '64bit':
            string = regex32.sub('', string)
            string = regex64.sub('\g<1>\n', string)
        else:
            string = regex64.sub('', string)
            string = regex32.sub('\g<1>\n', string)
        regex_random = re.compile(r'(\n.*?)\s+# random\s*\n.*$', re.MULTILINE)
        string = regex_random.sub('', string)
        # Adjust the name of the PariError exception
        # Remove deprecation warnings in the output
        string = re.sub('[ ]*doctest:...:[^\n]*\n', '', string)
        # Enable sage tests
        string = re.sub('sage:', '>>>', string)
        string = re.sub('\.\.\.\.:', '...', string)
        # Remove lines containing :: which confuse doctests
        string = re.sub(' ::', '                  ', string)
        return doctest.DocTestParser.parse(self, string, name)

extra_globals = dict([('pari', _pari.pari)])    
modules_to_test = [
    (_pari, extra_globals),
    (tests, extra_globals),
]

# Cython adds a docstring to _pari.__test__ *only* if it contains '>>>'.
# To enable running Sage doctests, with prompt 'sage:', we need to add
# docstrings containing no '>>>' prompt to _pari.__test__ ourselves.
# Unfortunately, line numbers are not readily available to us.
for cls in (_pari.Gen, _pari.Pari):
    for key, value in cls.__dict__.items():
        docstring = getattr(cls.__dict__[key], '__doc__')
        if isinstance(docstring, str):
            if docstring.find('sage:') >= 0 and docstring.find('>>>') < 0:
                _pari.__test__['%s.%s (line 0)'%(cls.__name__, key)] = docstring

# On Windows these tests segfault, presumably because the Pari stack gets
# deallocated when the test environment is destroyed.  Running the test commands
# by hand in the interpreter does not cause a crash.

if sys.platform == 'win32':
    _pari.__test__.pop('Pari.__init__ (line 0)')
    _pari.__test__.pop('Pari._close (line 0)')
    
def runtests(verbose=False):
    parser = DocTestParser()
    finder = doctest.DocTestFinder(parser=parser)
    failed, attempted = 0, 0
    for module, extra_globals in modules_to_test:
        print('Running doctests in %s:'%module.__name__)
        runner = doctest.DocTestRunner(
            verbose=verbose,
            optionflags=doctest.ELLIPSIS|doctest.IGNORE_EXCEPTION_DETAIL)
        count = 0
        for test in finder.find(module, extraglobs=extra_globals):
            count += 1
            runner.run(test)
        result = runner.summarize()
        failed += result.failed
        attempted += result.attempted
        print(result)
        print()
    print('\nAll doctests:\n   %s failures out of %s tests.' % (failed, attempted))
    return failed

if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'v', ['verbose'])
        opts = [o[0] for o in optlist]
        verbose = '-v' in opts
    except getopt.GetoptError:
        verbose = False
    failed = runtests(verbose)
    sys.exit(failed)

