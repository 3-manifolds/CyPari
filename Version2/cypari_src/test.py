import doctest, re, getopt, sys
from . import tests
from . import gen
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
        # Adjust the name of the PariError exception
        if sys.version_info.major < 3:
            ## Why does this fail with re.MULTILINE????
            string = re.sub('cypari_src.gen.PariError', 'PariError', string)
        # Enable sage tests
            string = re.sub('sage:', '>>>', string, re.MULTILINE)
        # Remove lines containing :: which confuse doctests
            string = re.sub('::', '                  ', string, re.MULTILINE)
        return doctest.DocTestParser.parse(self, string, name)

extra_globals = dict([('pari', gen.pari)])    
modules_to_test = [
#    (pari_instance, extra_globals),
    (gen, extra_globals),
    (tests, extra_globals),
]

# Cython adds a docstring to gen.__test__ *only* if it contains '>>>'.
# To enable running Sage doctests, with prompt 'sage:' we need to add
# some docstrings to gen.__test__

for cls in (gen.Gen, gen.Pari):
    for key, value in cls.__dict__.items():
        docstring = getattr(cls.__dict__[key], '__doc__')
        if isinstance(docstring, str):
            if docstring.find('Sage:') >= 0 and docstring.find('>>>') < 0:
                gen.__test__['%s.%s'%(cls.__name__, key)] = docstring

def runtests(verbose=False):
    finder = doctest.DocTestFinder(parser=DocTestParser())
    failed, attempted = 0, 0
    for module, extra_globals in modules_to_test:
        runner = doctest.DocTestRunner(verbose=verbose,
                                       optionflags=doctest.ELLIPSIS)
        for test in finder.find(module, extraglobs=extra_globals):
            runner.run(test)
        result = runner.summarize()
        print(result)
        failed += result.failed
        attempted += result.attempted
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

