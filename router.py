
import sys
import argparse

from parser import Parser 

class Router:
    """
    The router collects all the input data and prepares it for parsing.
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: options
    # Command line arguments
    options = None

    # Property: output
    # The rendered output
    output = ''

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, version):
        self.version = version

    # Methods
    # ------------------------------------------------------------------

    def parse_args(self, options=sys.argv[1:]):
        print 'parge_args(): options: ', options
        global version

        parser = argparse.ArgumentParser(
            description='Parses and tokenizes text.',
            epilog='Refer to the documentation for more detailed information.',
            prog=sys.argv[0],
            )

        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s ' + self.version,
                            help='print the version information and exit')

        parser.add_argument('input', metavar='INPUT', type=str, nargs='?',
                            help='input string')

        parser.add_argument('--inputfile', type=str, metavar='FILE',
                            help='input file')

        args = parser.parse_args(options)

        print 'parge_args(): ', repr(args)
        self.options = args

    def start(self):
        #~ import pdb; pdb.set_trace()
        filestr = inputstr = ''

        print 'start(): self.options: ', repr(self.options)

        if (self.options.inputfile):
            print 'adding file'
            try:
                f = open(self.options.inputfile, 'rb')
                #self.input = [x.strip() for x in f if x.strip()]
                filestr = f.read()
                f.close()

            except IOError:
                print 'Could not read file.', sys.exc_info()[1]
                self.exit()

        if (self.options.input):
            print 'adding input'
            inputstr = self.options.input

        self.render(('\n'.join((filestr, inputstr))).strip())

    def render(self, str=None):
        print 'parse() str: %s "%s"' % (type(str), str)

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

        try:
            self.parser = Parser(lines)
            #self.parser.load_string(lines)
            self.output = self.parser.parse()

        # todo: add actual exception handler
        except:
            sys.stderr.write("Parse error. Check your input.")
            print sys.exc_info()[0]
            print sys.exc_info()[1]

    def exit(self):
        sys.exit()
