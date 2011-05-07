
import sys
import argparse

from question import Question

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

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        options = None
        questions = ''

    # Public methods
    # ------------------------------------------------------------------

    def setup(self, options):
        parser = argparse.ArgumentParser(
            description='Parses and tokenizes text.',
            epilog='Refer to the documentation for more detailed information.',
            prog=sys.argv[0],
            )

        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s Router version ' + self.version,
                            help='print the version information and exit')

        parser.add_argument('-s', '--silent', action='store_true',
                            help='do not print out statistical information')

        parser.add_argument('-q', '--qualify', action='store_true',
                            help='Qualify the output with the question parts') # e.g. "stem = ...."

        parser.add_argument('-i', dest='inputfile', type=str, metavar='INFL',
                            help='input filename')

        parser.add_argument('-o', dest='outputfile', type=str, metavar='OUFL',
                            help='output filename')

        parser.add_argument('-p', dest='parser', type=str, metavar='PRSR',
                            help='parser class')

        parser.add_argument('-f', dest='filters', type=str, metavar='FLTRs',
                            help='filterer classes "F1, F2,... Fn"')

        parser.add_argument('-w', dest='writer', type=str, metavar='WRTR',
                            help='writer class')

        parser.add_argument('input', metavar='INPUT', type=str, nargs='?',
                            help='input string')

        self.options = parser.parse_args(options)

        # 'asdf , qwer' ==>> ['asdf', 'qwer']
        self.options.filters = [f.strip() for f in self.options.filters.split(',')] if self.options.filters else []

    def start(self, options=sys.argv[1:]):
        #~ import pdb; pdb.set_trace()
        self.setup(options)

        self._parse(self._get_input())

        if not self.options.silent:
            self._show_stats()

        self._filter()
        self._write()

    # Protected methods
    # ------------------------------------------------------------------

    def _parse(self, string):
        try:
            if string:
                self.parser = self._get_parser(string)
                print 'parser: %s' % self.parser
                self.questions = self.parser.parse()

        except AttributeError:
            sys.stderr.write("Could not parse input, bad parser selected.")
            print sys.exc_info()[1]
            return

    def _filter(self):
        try:
            self.filters = self._get_filters()

        except AttributeError:
            sys.stderr.write("Could not declare filters.")
            print sys.exc_info()[1]
            return

        for filter in self.filters:
            print 'filter: %s' % filter
            self.questions = filter.filter(self.questions)

    def _write(self):
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

    def _get_input(self):
        #~ import pdb; pdb.set_trace()

        if self.options.inputfile:
            try:
                f = open(self.options.inputfile, 'rb')
                filestr = f.read()
                f.close()
                # note: any command line input is ignored
                return filestr

            except IOError:
                print 'Could not read file.', sys.exc_info()[1]
                self._exit()

        if self.options.input:
            return self.options.input

        try:
            print 'Enter input text (ctrl-D to end)'
            return sys.stdin.read()

        except KeyboardInterrupt:
            pass

    def _get_parser(self, string):
        parser = self.options.parser if self.options.parser else 'SingleParser'
        #~ Parser = type(parser, (), {})
        Parser = self.__forname("parser", parser)
        if Parser:
            return Parser(string)

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

    def _show_stats(self):
        #~ import pdb; pdb.set_trace()
        print 'stats: self.options: ', repr(self.options)
        print 'stats: %d question%s found.' % (len(self.questions), 's' if len(self.questions) != 1 else '')

        for question in self.questions:
            print 'stats: stem is %d bytes long, %d option%s found.' % (
                len(question.stem),
                len(question.options),
                's' if len(question.options) != 1 else ''
                )

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
