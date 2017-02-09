import doctest, re, getopt, sys
from . import tests
from . import gen
import sys, platform
if sys.version_info.major == 2:
    from . import py2tests
else:
    from . import py3tests

cpu_width = platform.architecture()[0]

class DocTestParser(doctest.DocTestParser):
    def parse(self, string, name='<string>'):
        regex32 = re.compile(r'(\n.*?)\s+# 32-bit\s*$', re.MULTILINE)
        regex64 = re.compile(r'(\n.*?)\s+# 64-bit\s*$', re.MULTILINE)
        if cpu_width == '64bit':
            string = regex32.sub('', string)
            string = regex64.sub('\g<1>', string)
        else:
            string = regex64.sub('', string)
            string = regex32.sub('\g<1>', string)
        if sys.version_info.major < 3:
            string = re.sub('cypari_src.gen.PariError', 'PariError', string)
        return doctest.DocTestParser.parse(self, string, name)

extra_globals = dict([('pari', gen.pari)])    
modules_to_test = [
#    (pari_instance, extra_globals),
    (gen, extra_globals),
    (tests, extra_globals),
]


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

