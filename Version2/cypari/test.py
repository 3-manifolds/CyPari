import doctest
import re
from . import tests
from . import pari

class DocTestParser(doctest.DocTestParser):
    def parse(self, string, name='<string>'):
        string, num = re.subn('([\n\A]\s*)sage:', '\g<1>>>>', string)
        string, num = re.subn('\.\.\.\.:', '...', string)
        return doctest.DocTestParser.parse(self, string, name)

if __name__ == '__main__':
    finder = doctest.DocTestFinder(parser=DocTestParser())
    extra_globals = dict([('pari',pari)])
    runner = doctest.DocTestRunner(verbose=False)
    for test in finder.find(tests, extraglobs=extra_globals):
        runner.run(test)
    print runner.summarize()

