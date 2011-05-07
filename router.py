
import sys
import argparse

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

        parser.add_argument('--inputfile', type=str, metavar='INFL',
                            help='input filename')

        parser.add_argument('--outputfile', type=str, metavar='OUFL',
                            help='output filename')

        parser.add_argument('--parser', type=str, metavar='PRSR',
                            help='parser class')

        parser.add_argument('--filter', type=str, metavar='FLTR',
                            help='filterer class')

        parser.add_argument('--writer', type=str, metavar='WRTR',
                            help='writer class')

        parser.add_argument('input', metavar='INPUT', type=str, nargs='?',
                            help='input string')

        self.options = parser.parse_args(options)

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
                self.questions = self.parser.parse()

        except AttributeError:
            sys.stderr.write("Could not parse input, bad parser selected.")
            print sys.exc_info()[1]
            return

    def _filter(self):
        try:
            self.filterer = self._get_filterer()

        except AttributeError:
            sys.stderr.write("Could not declare filterer.")
            print sys.exc_info()[1]
            return
            
        self.questions = self.filterer.filter(self.questions)

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
        filestr = inputstr = ''

        if self.options.inputfile:
            try:
                f = open(self.options.inputfile, 'rb')
                #self.input = [x.strip() for x in f if x.strip()]
                filestr = f.read()
                f.close()

            except IOError:
                print 'Could not read file.', sys.exc_info()[1]
                self._exit()

        if self.options.input:
            inputstr = self.options.input

        string = ('\n'.join((filestr, inputstr))).strip()
        if string: 
            return string

        try:
            print 'Enter input text (ctrl-D to end)'
            return " ".join([sys.stdin.read()])

        except KeyboardInterrupt:
            pass

    def _get_parser(self, string):
        parser = self.options.parser if self.options.parser else 'SingleParser'
        #~ Parser = type(parser, (), {})
        Parser = self.__forname("parser", parser)
        return Parser(string)

    def _get_filterer(self):
        filter = self.options.filter if self.options.filter else 'WhitespaceFilter'
        Filter = self.__forname("filter", filter)
        return Filter()

    def _get_writer(self):
        writer = self.options.writer if self.options.writer else 'TextWriter'
        Writer = self.__forname("writer", writer)
        return Writer()

    def _show_stats(self):
        #~ import pdb; pdb.set_trace()
        print 'stats: self.options: ', repr(self.options)
        print 'stats: %d questions found.' % len(self.questions)

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
        module = __import__(modname)
        classobj = getattr(module, classname)
        return classobj

########################################################################
class Question(object):
    """
    A question is composed of a stem and a list of options.
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: stem
    # The so-called question
    stem = ''

    # Property: options
    # The list of possible selections
    options = []

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        self.stem = ''
        self.options = []

    def __str__(self):
        return '%s %d' % (self.stem, len(self.options))
