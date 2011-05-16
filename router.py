
import sys
import argparse

from subprocess import Popen, PIPE, STDOUT
from question import Question
from question import Questions

########################################################################
class Router(object):
    """
    The router collects all the input data and prepares it for parsing.
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: version
    # Router version
    version = "0.1"

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
                            version='%(prog)s Router version ' + self.version,
                            help='print the version information and exit')

        command_line.add_argument('-v', '--verbose', action='store_true',
                            help='verbose output including doc-testing')

        command_line.add_argument('-s', '--silent', action='store_true',
                            help='do not print out statistical information')

        command_line.add_argument('-q', '--qualify', action='store_true',
                            help='Qualify the output with the question parts') # e.g. "stem = ...."

        command_line.add_argument('-i', dest='inputfile', type=str, metavar='INFL',
                            help='input filename')

        command_line.add_argument('-o', dest='outputfile', type=str, metavar='OUFL',
                            help='output filename')

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
        #~ import pdb; pdb.set_trace()
        self.setup(options)
        
        mogrifyed_input = self.mogrify(self.get_input())

        self.parse(mogrifyed_input)

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
        try:
            self.mogrifyers = list(self._get_mogrifyers())

        except AttributeError:
            sys.stderr.write("Could not declare mogrifyers.")
            print sys.exc_info()[1]
            return

        for mogrifyer in self.mogrifyers:
            string = mogrifyer.mogrify(string)
            
        return string

    def parse(self, string):
        try:
            if string:
                self.parser = self._get_parser(string)
                self.questions = self.parser.parse(string)

        except AttributeError:
            sys.stderr.write("Could not parse input, bad parser selected.")
            print sys.exc_info()[1]
            return

    def filter(self):
        try:
            self.filters = list(self._get_filters())

        except AttributeError:
            sys.stderr.write("Could not declare filters.")
            print sys.exc_info()[1]
            return

        for filter in self.filters:
            self.questions = filter.filter(self.questions)

    def write(self):
        try:
            self.writer = self._get_writer()

        except AttributeError:
            sys.stderr.write("Could not declare writer.")
            print sys.exc_info()[1]
            return

        if self.options.outputfile:
            try:
                output = open(self.options.outputfile + self.writer.extension, 'wb')

            except:
                sys.stderr.write("Could not open output file for writing.")
                print sys.exc_info()[1]
                return

        else:
            output = sys.stdout

        self.writer.write(output, self.questions)

        if self.options.outputfile:
            output.close()

    def get_input(self, inputfile=None):
        #~ import pdb; pdb.set_trace()

        inputfile = self.options.inputfile if not inputfile else inputfile
        if inputfile:
            # note: any command line input is ignored
            return self._get_file_contents(inputfile)

        if self.options.input:
            return self.options.input

        try:
            print 'Enter input text (ctrl-D to end)'
            return sys.stdin.read()

        except KeyboardInterrupt:
            pass

    def show_stats(self):
        #~ import pdb; pdb.set_trace()
        print 'stats: self.options: ', repr(self.options)
        print 'stats: qhash: ', self.qhash
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

    def _get_file_contents(self, inputfile):
        if '.pdf' == inputfile[len(inputfile)-4:len(inputfile)]:
            command_line = ['pdftotext', '-raw', inputfile, '-']
            proc = Popen(command_line, stdout=PIPE, stderr=STDOUT)
            out, err = proc.communicate()
            #~ print 'out=(%s), err=(%s)' % (out, err)
            return err if err else out

        try:
            f = open(inputfile, 'r')
            filestr = f.read()
            f.close()
            return filestr

        except IOError:
            print 'Could not read file.', sys.exc_info()[1]
            self._exit()

    def _get_mogrifyers(self):
        for mogrifyer in self.options.mogrifyers:
            Mogrifyer = self.__forname("mogrifyer", mogrifyer)
            if Mogrifyer:
                yield Mogrifyer()

    def _get_parser(self, string):
        #parser = self.options.parser if self.options.parser else 'SingleParser'
        if self.options.parser: 
            return self.__forname("parser", self.options.parser)()

        #~ import pdb; pdb.set_trace()
        #~ Parser = type(parser, (), {})
        for parserclass in ('SingleParser', 'IndexParser', 'BlockParser'):
            Parser = self.__forname("parser", parserclass)
            self.qhash[parserclass] = Questions(Parser().parse(string))

        if   self.qhash['IndexParser'].length > 1 and self.qhash['IndexParser'].symetrical:
            parser = 'IndexParser'
        elif self.qhash['BlockParser'].length > 1 and self.qhash['BlockParser'].symetrical:
            parser = 'BlockParser'
        elif self.qhash['IndexParser'].length > 1:
            parser = 'IndexParser'
        else:
            parser = 'SingleParser'
            
        return self.__forname("parser", parser)()

    def _get_filters(self):
        for filter in self.options.filters:
            Filter = self.__forname("filter", filter)
            if Filter:
                yield Filter()

        # -q command line switch is a shortcut for the QualifiedFilter filter
        if self.options.qualify:
            Filter = self.__forname("filter", 'QualifiedFilter')
            if Filter:
                yield Filter()

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
            print modname, sys.exc_info()[1]
