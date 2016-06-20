import doctest, re, getopt, sys
from . import tests
from . import gen
from . import pari_instance

class DocTestParser(doctest.DocTestParser):
    def parse(self, string, name='<string>'):
        string, num = re.subn('([\n\A]\s*)sage:', '\g<1>>>>', string)
        string, num = re.subn('\.\.\.\.:', '...', string)
        return doctest.DocTestParser.parse(self, string, name)

extra_globals = dict([('pari', pari_instance.pari)])    
modules_to_test = [
    (tests, extra_globals),
    (pari_instance, extra_globals),
    # (gen, extra_globals)
]


if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'v', ['verbose'])
        opts = [o[0] for o in optlist]
        verbose = '-v' in opts
    except getopt.GetoptError:
        verbose = False
    
    finder = doctest.DocTestFinder(parser=DocTestParser())
    failed, attempted = 0, 0
    runner = doctest.DocTestRunner(verbose=verbose)
    for module, extra_globals in modules_to_test:
        for test in finder.find(module, extraglobs=extra_globals):
            runner.run(test)
        result = runner.summarize()
        print(result)
        failed += result.failed
        attempted += result.attempted
    print('\nAll doctests:\n   %s failures out of %s tests.' % (failed, attempted))




