import doctest
import re
from . import tests
from . import pari
from . import gen
from . import pari_instance

class DocTestParser(doctest.DocTestParser):
    def parse(self, string, name='<string>'):
        string, num = re.subn('([\n\A]\s*)sage:', '\g<1>>>>', string)
        string, num = re.subn('\.\.\.\.:', '...', string)
        return doctest.DocTestParser.parse(self, string, name)

if __name__ == '__main__':
    finder = doctest.DocTestFinder(parser=DocTestParser())
    extra_globals = dict([('pari',pari)])
    failed, attempted = 0, 0
    runner = doctest.DocTestRunner(verbose=False)
    for module in [tests, pari_instance]:   # Adding gen causes segfault on OS X
        for test in finder.find(module, extraglobs=extra_globals):
            runner.run(test)
        result = runner.summarize()
        print(result)
        failed += result.failed
        attempted += result.attempted
    print('\nAll doctests:\n   %s failures out of %s tests.' % (failed, attempted))




