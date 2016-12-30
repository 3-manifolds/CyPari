import doctest, re, getopt, sys
from . import tests
from . import gen
    
class DocTestParser(doctest.DocTestParser):
    def parse(self, string, name='<string>'):
        string, num = re.subn('([\n\A]\s*)sage:', '\g<1>>>>', string)
        string, num = re.subn('\.\.\.\.:', '...', string)
        return doctest.DocTestParser.parse(self, string, name)

extra_globals = dict([('pari', gen.pari)])    
modules_to_test = [
#    (pari_instance, extra_globals),
    (gen, extra_globals),
    (tests, extra_globals),
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
    runner = doctest.DocTestRunner(verbose=verbose,
                                   optionflags=doctest.ELLIPSIS)
    for module, extra_globals in modules_to_test:
        for test in finder.find(module, extraglobs=extra_globals):
            runner.run(test)
        result = runner.summarize()
        print(result)
        failed += result.failed
        attempted += result.attempted
    print('\nAll doctests:\n   %s failures out of %s tests.' % (failed, attempted))




