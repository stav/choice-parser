
import sys
import argparse

#from parser import SingleParser as Parser
from parser import IndexParser as Parser

class Router:
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

    # Property: output
    # The rendered output
    output = ''

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        pass

    # Methods
    # ------------------------------------------------------------------

    def parse_args(self, options=sys.argv[1:]):
        global version

        parser = argparse.ArgumentParser(
            description='Parses and tokenizes text.',
            epilog='Refer to the documentation for more detailed information.',
            prog=sys.argv[0],
            )

        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s Router version ' + self.version,
                            help='print the version information and exit')

        parser.add_argument('input', metavar='INPUT', type=str, nargs='?',
                            help='input string')

        parser.add_argument('--inputfile', type=str, metavar='FILE',
                            help='input file')

        args = parser.parse_args(options)

        self.options = args

    def start(self):
        #~ import pdb; pdb.set_trace()
        filestr = inputstr = ''

        print 'start(): self.options: ', repr(self.options)

        if (self.options.inputfile):
            try:
                f = open(self.options.inputfile, 'rb')
                #self.input = [x.strip() for x in f if x.strip()]
                filestr = f.read()
                f.close()

            except IOError:
                print 'Could not read file.', sys.exc_info()[1]
                self.exit()

        if (self.options.input):
            inputstr = self.options.input

        self.render(('\n'.join((filestr, inputstr))).strip())

    def render(self, str=None):
        try:
            if str:
                lines = str
            else:
                print 'Enter input text (ctrl-D to end)'
                lines = [sys.stdin.read()]
                lines = " ".join(lines)

        except KeyboardInterrupt:
            pass

        # todo: add actual exception handler
        except:
            sys.stderr.write("Reading failed.\n")
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            return

        self.parser = Parser(lines)
        #self.parser.load_string(lines)
        self.questions = self.parser.parse()

        print 'stats: %d questions found.' % len(self.questions)

        for question in self.questions:
            print 'stats: stem is %d bytes long, %d option%s found.' % (
                len(question.stem),
                len(question.options),
                's' if len(question.options) != 1 else ''
                )

    def exit(self):
        sys.exit()
