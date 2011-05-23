
import sys
import argparse

from subprocess import Popen, PIPE, STDOUT
from question import Question
from question import Questions

########################################################################
class Router(object):
    """
    The router collects all the input data and prepares it for parsing.

    Method map::

        start()

            load()
                setup()
                get_input()
                mogrify()
                parse()
                filter()
                show-stats()

            write()
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: version
    # Router version
    version = '0.1'

    # Property: develenv
    # Development enviroment
    develenv = 'Python 2.7.1+ (r271:86832, Apr 11 2011, 18:05:24) [GCC 4.5.2] on linux2'

    # Property: options
    # Command line arguments
    options = None

    # Property: questions
    # The list of questions
    questions = ''

    # Property: qhash
    # A numerical description of the parsed list of questions
    qhash = {}

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        self.questions = ''
        self.qhash     = {}
        self.options   = None
        self.parser    = None
        self.mogrifyers= []
        self.filters   = []

    # Public methods
    # ------------------------------------------------------------------

    def setup(self, options):
        """
        >>> options = ['--qualify']
        >>> r = Router()
        >>> r.setup(options)
        >>> r.options
        Namespace... qualify=True...
        """
        # declare command-line argument parser
        command_line = argparse.ArgumentParser(
            description='Parses and tokenizes text.',
            epilog='Refer to the documentation for more detailed information.',
            prog=sys.argv[0],
            )

        # define the command-line arguments
        command_line.add_argument('-V', '--version', action='version',
                            version='%(prog)s Router version ' + self.version + ' developed with ' + self.develenv,
                            help='print the version information and exit')

        command_line.add_argument('-v', '--verbose', action='store_true',
                            help='verbose output including doc-testing')

        command_line.add_argument('-s', '--silent', action='store_true',
                            help='do not print out statistical information')

        command_line.add_argument('-q', '--qualify', action='store_true',
                            help='Qualify the output with the question parts') # e.g. "stem = ...."

        command_line.add_argument('-i', dest='inputfile', nargs='?', metavar='INFL',
                            type=argparse.FileType('r'), default=sys.stdin,
                            help='input filename, def=stdin')

        command_line.add_argument('-o', dest='outputfile', metavar='OUFL', nargs='?',
                            type=argparse.FileType('w'), default=sys.stdout, const='/dev/null',
                            help='output filename, def=stdout, const=/dev/null')

        command_line.add_argument('-m', dest='mogrifyers', type=str, metavar='MGRFs',
                            help='mogrifyer classes "M1, M2,... Mn"')

        command_line.add_argument('-p', dest='parser', type=str, metavar='PRSR',
                            help='parser class')

        command_line.add_argument('-f', dest='filters', type=str, metavar='FLTRs',
                            help='filterer classes "F1, F2,... Fn"')

        command_line.add_argument('-w', dest='writer', type=str, metavar='WRTR',
                            help='writer class')

        command_line.add_argument('input', metavar='INPUT', type=str, nargs='?',
                            help='input string')

        # load the commandline options
        self.options = command_line.parse_args(options)

        # 'asdf , qwer' ==>> ['asdf', 'qwer']
        self.options.filters    = [f.strip() for f in self.options.filters.split(',')   ] if self.options.filters    else []
        self.options.mogrifyers = [m.strip() for m in self.options.mogrifyers.split(',')] if self.options.mogrifyers else []

    def load(self, options=sys.argv[1:]):
        """
        The primary Router method to handle: setup, mogrifying, parsing and
        filtering.

        >>> r = Router()
        >>> r.load(['-s', '''This is the stem
        ... This is an option'''])
        >>> len(r.questions)
        1
        """
        self.setup(options)

        self.parse (self.mogrify (self.get_input ()))

        self.filter()

        if not self.options.silent:
            self.show_stats()

    def start(self, options=sys.argv[1:]):
        """
        Loads input and writes output.

        >>> r = Router()
        >>> r.start(['''This is the stem
        ... This is an option'''])
        stats: ...
        stats: 1 question found.
        stats: stem is 16 bytes long, 1 option found.
        This is the stem
        This is an option
        """
        self.load(options)
        self.write()

    def mogrify(self, string):
        """
        Load all mogrifiers specified on the command-line and apply them
        one at a time to the input string returning the mogrified string.
        A mogrifier takes an input string and applies some search and replace
        logic usually to massage the string into a different format: removing
        all non-printable characters, for example.

        @param  string  string  The input string to mogrify
        @return  string  The mogrified string

        >>> from mogrifyer import BooleanoptionMogrifyer
        >>> r = Router()
        >>> r.setup(['-m', 'BooleanoptionMogrifyer'])
        >>> print r.mogrify('''This is the stem
        ... yes no a. This is an option''')
        This is the stem
        a. This is an option
        """
        self.mogrifyers = list(self._get_mogrifyers())

        for mogrifyer in self.mogrifyers:
            string = mogrifyer.mogrify(string)

        return string

    def parse(self, string):
        """
        The parsing is the heart of the router and here we run the protected
        method _get_parser() to determine the best parser to, instantiate
        and object instance for us which we run the parse() method on to
        retrieve our question list which we load into ourself.

        @param  string  string  The mogrified input string

        >>> r = Router()
        >>> r.setup([])
        >>> r.parse('''This is the stem
        ... This is an option''')
        >>> assert len(r.questions) == 1
        >>> print r.questions[0].stem
        This is the stem
        """
        try:
            if string:
                self.parser = self._get_parser(string)
                self.questions = self.parser.parse(string)

        except AttributeError:
            sys.stderr.write("Could not parse input. ")
            print sys.exc_info()[1]

    def filter(self):
        """
        Load all filters specified on the command-line and apply them
        one at a time to the parsed question list.

        >>> r = Router()
        >>> r.setup(['-f', 'IndexFilter'])
        >>> r.parse('1. This is the stem')
        >>> print r.questions[0].stem
        1. This is the stem
        >>> r.filter()
        >>> print r.questions[0].stem
         This is the stem
        """
        self.filters = list(self._get_filters())

        for filter in self.filters:
            self.questions = filter.filter(self.questions)

    def write(self):
        try:
            writer = self._get_writer()

        except AttributeError:
            sys.stderr.write("Could not declare writer.")
            print sys.exc_info()[1]
            return

        writer.write(self.options.outputfile, self.questions)

        #self.options.outputfile.close() # only close if not stdout

    def get_input(self, inputfile=None):
        """
        Return the input from the command-line. If an inputfile is designated
        then return that file's contents.  Otherwise, if no input is specified
        then read from standard input.

        @param  inputfile  File  The open input file object
        @return  string  The input

        >>> r = Router()
        >>> r.setup(['''This is the stem
        ... This is an option'''])
        >>> print r.get_input()
        This is the stem
        This is an option
        """
        if self.options and self.options.input:
            # note: any file input is ignored
            return self.options.input

        inputfile = self.options.inputfile if not inputfile else inputfile

        return self._read(inputfile)

    def show_stats(self):
        """
        Display internal statistics.  Silenced with the -s switch.
        """
        print 'stats: self.options: ', repr(self.options)
        print 'stats: qhash: ', self.qhash
        print 'stats: mogrifyers: %s' % self.mogrifyers
        print 'stats: parser: %s' % self.parser
        print 'stats: filters: %s' % self.filters
        print 'stats: %d question%s found.' % (len(self.questions), 's' if len(self.questions) != 1 else '')

        for question in self.questions:
            print 'stats: stem is %d bytes long, %d option%s found.' % (
                len(question.stem),
                len(question.options),
                's' if len(question.options) != 1 else ''
                )

    # Protected methods
    # ------------------------------------------------------------------

    def _read(self, inputfile):
        """
        A wrapper for inputfile.read() to trap for the PDF conversion
        """
        if '.pdf' == inputfile.name[len(inputfile.name)-4:len(inputfile.name)]:
            command_line = ['pdftotext', '-raw', inputfile.name, '-']
            proc = Popen(command_line, stdout=PIPE, stderr=STDOUT)
            out, err = proc.communicate()
            return err if err else out

        return inputfile.read()

    def _get_mogrifyers(self):
        for mogrifyer in self.options.mogrifyers:
            try:
                Mogrifyer = self.__forname("mogrifyer", mogrifyer)
            except AttributeError:
                print 'mogrifyer', sys.exc_info()[1]
            else:
                yield Mogrifyer()

        yield self.__forname("mogrifyer", 'SplitstemMogrifyer')()

    def _get_parser(self, string=''):
        """
        This tries to use some rudimentary intelligence to determine which
        parser to choose based on how many questsions it parses out giving
        extra weight to a uniform distribution of options.

        @param  string  string  The input string for the parsers to parse
        @return  parser.Parser  The selected parser instantiation

        >>> r = Router()
        >>> r.setup(['-p', 'IndexParser'])
        >>> r._get_parser()
        <parser.IndexParser object at...
        """
        if self.options.parser:
            return self.__forname("parser", self.options.parser)()

        # run all the parsers for the input string and load the results
        # into a hash.
        for parserclass in ('IndexParser', 'BlockParser', 'ChunkParser'):
            Parser = self.__forname("parser", parserclass)
            self.qhash[parserclass] = Questions(Parser().parse(string))

        # now look at the parser results to determine which one to use.
        # we first look for an ordered IndexParser and then for an ordered
        # ChunkParser otherwise we look for a symetrical IndexParser and
        # then a symetrical IndexParser and so on.
        if   False: parser = ''
        elif self.qhash['IndexParser'].length > 1 and self.qhash['IndexParser'].ordered: parser = 'IndexParser'
        elif self.qhash['ChunkParser'].length > 1 and self.qhash['ChunkParser'].ordered: parser = 'ChunkParser'
        elif self.qhash['BlockParser'].length > 1 and self.qhash['BlockParser'].ordered: parser = 'BlockParser'

        elif self.qhash['IndexParser'].length > 1 and self.qhash['IndexParser'].symetrical: parser = 'IndexParser'
        elif self.qhash['ChunkParser'].length > 1 and self.qhash['ChunkParser'].symetrical: parser = 'ChunkParser'
        elif self.qhash['BlockParser'].length > 1 and self.qhash['BlockParser'].symetrical: parser = 'BlockParser'

        elif self.qhash['IndexParser'].length > 1: parser = 'IndexParser'
        elif self.qhash['ChunkParser'].length > 1: parser = 'ChunkParser'
        else:
            parser = 'SingleParser'

        return self.__forname("parser", parser)()

    def _get_filters(self):
        for filter in self.options.filters:
            try:
                Filter = self.__forname("filter", filter)
            except AttributeError:
                print 'filter', sys.exc_info()[1]
            else:
                yield Filter()

        # -q command line switch is a shortcut for the QualifiedFilter filter
        if self.options.qualify:
            yield self.__forname("filter", 'QualifiedFilter')()

    def _get_writer(self):
        writer = self.options.writer if self.options.writer else 'TextWriter'
        Writer = self.__forname("writer", writer)
        if Writer:
            return Writer()

    def _exit(self):
        sys.exit()

    # Private methods
    # ------------------------------------------------------------------

    def __forname(self, modname, classname):
        """
        Returns a class of "classname" from module "modname".
        reposted by ben snider
            from http://mail.python.org/pipermail/python-list/2003-March/192221.html
              on http://www.bensnider.com/2008/02/27/dynamically-import-and-instantiate-python-classes/
        """
        try:
            module = __import__(modname)
            classobj = getattr(module, classname)
            return classobj

        except AttributeError:
            raise