
import sys
import pprint
import argparse

from subprocess import Popen, PIPE, STDOUT
from os         import path

from question import Question
from question import Questions

try:
    from pyPdf import PdfFileReader # external library
    
except ImportError:
    PdfFileReader = None

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
                <show stats>

            write()
    """

    # Properties
    # ------------------------------------------------------------------

    version = '0.1'
    develenv = 'Python 2.7.1+ (r271:86832, Apr 11 2011, 18:05:24) [GCC 4.5.2] on linux2'

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        self.questions = []
        self.new_questions = {}
        self.qhash     = {}
        self.inputs    = {}
        self.options   = None
        self.parser    = None
        self.mogrifyers= []
        self.filters   = []
        self.PrettyPrinter = pprint.PrettyPrinter(indent=4, width=72)
        self.setup([])

    # Magic methods
    # ------------------------------------------------------------------

    def __str__(self):
        infile = self.options.inputfile 
        tokens = self.parser.tokens if self.parser and self.options.stats > 2 else []
        toklen = 72 if self.options.stats < 4 else 999
        f      = self.PrettyPrinter.pformat if self.options.stats > 1 else str
        questions = ['%s question %d' % (self.questions[i], i+1) for i in range(0, len(self.questions))] if self.options.stats > 4 else []

        string = '''<%s.%s, questions=%d>
%s
input: %s, %s, mode %s,%s encoding %s, newlines %s
%s
mogrifyers: %s
filters: %s
parser: %s
tokens: %s
%s
%s
new: %s
        ''' % (
            __name__,
            self.__class__.__name__,
            len(self.questions),
# options
            f(vars(self.options)),
# input
            infile.name,
            'closed' if infile.closed else 'open',
            infile.mode,
            ' size %d,' % path.getsize(infile.name) if infile != sys.stdin else '',
            infile.encoding,
            repr(infile.newlines),
# qhash & formatters
            f(self.qhash),
            f(self.mogrifyers),
            f(self.filters),
# parser
            f(str(self.parser)),
            f(['%-80s token %2d' % (tokens[i][0:toklen] + ('...' if len(tokens[i]) > toklen else ''), i+1) for i in range(0, len(tokens))]),
            f({'questions': Questions(self.questions)}),
            '\n'.join(questions),
            f(self.new_questions)
            )

        return unicode(string).encode('ascii', 'replace')   # replaces with ?
        #~ print s.encode('ascii', 'ignore')    # removes the unicode chars
        #~ print s.encode('ascii', 'replace')   # replaces with ?
        #~ print s.encode('ascii', 'xmlcharrefreplace') # turn into xml entities
        #~ print s.encode('ascii', 'strict')    # throw UnicodeEncodeErrors

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

        command_line.add_argument('-s', '--stats', nargs='?', metavar='SLVL',
                            type=int, default=0, const=1,
                            help='stats print level: 1, 2, 3, 4, 5 (5=most)')

        command_line.add_argument('-q', '--qualify', action='store_true',
                            help='Qualify the output with the question parts') # e.g. "stem = ...."

        command_line.add_argument('-i', dest='inputfile', nargs='?', metavar='INFL',
                            type=argparse.FileType('rU'), default=sys.stdin,
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

        # 'foo , bar' ==>> ['foo', 'bar']
        self.options.filters    = [f.strip() for f in self.options.filters.split(',')   ] if self.options.filters    else []
        self.options.mogrifyers = [m.strip() for m in self.options.mogrifyers.split(',')] if self.options.mogrifyers else []

    def load(self, options=sys.argv[1:]):
        """
        The primary Router method to handle: setup, mogrifying, parsing and
        filtering.

        >>> r = Router()
        >>> r.load(['''This is the stem
        ... This is an option'''])
        >>> len(r.questions)
        1
        """
        try:
            self.setup(options)

        except SystemExit:
            pass

        else:
            self.stow()
            self.mogrify()
            self.parse()
            self.filter()

            if self.options.stats:
                print self

    def start(self, options=sys.argv[1:]):
        """
        Loads input and writes output.

        >>> r = Router()
        >>> r.start(['''This is the stem
        ... This is an option'''])
        This is the stem
        This is an option
        """
        self.load(options)
        self.write()

    def mogrify(self):
        """
        Load all mogrifiers specified on the command-line and apply them
        one at a time to the input string returning the mogrified string.
        A mogrifier takes an input string and applies some search and replace
        logic usually to massage the string into a different format: removing
        all non-printable characters, for example.

        >>> from mogrifyer import BooleanoptionMogrifyer
        >>> r = Router()
        >>> r.setup(['-m', 'BooleanoptionMogrifyer'])
        >>> print r.mogrify(['''This is the stem
        ... yes no a. This is an option'''])[0]
        This is the stem
        a. This is an option
        """
        self.mogrifyers = list(self._get_mogrifyers())

        for type in self.inputs:
            for mogrifyer in self.mogrifyers:
                self.inputs[type] = mogrifyer.mogrify(self.inputs[type])

    def parse(self):
        """
        The parsing is the heart of the router and here we run the protected
        method _get_parser() to determine the best parser to, instantiate
        and object instance for us which we run the parse() method on to
        retrieve our question list which we load into ourself.

        ..note: This is doing double work if get_parser() is running all
        the parsers.

        >>> r = Router()
        >>> r.parse(['''This is the stem
        ... This is an option'''])
        >>> assert len(r.questions) == 1
        >>> print r.questions[0].stem
        This is the stem
        """
        def listify(o):
             return o if type(o) == list else [o]

        for input_type in self.inputs:
            strings = listify(self.inputs[input_type])
            try:
                self.parser = self._get_parser(strings)
                #~ import pdb; pdb.set_trace()
                for string in strings:
                    self.parser.parse(string)

            except (AttributeError, OverflowError, OSError):
                self.__error(("Could not parse input.", self.parser, sys.exc_info()[1]))

            self.questions.extend(self.parser.questions)
            self.new_questions[input_type] = self.parser.questions

    def filter(self):
        """
        Load all filters specified on the command-line and apply them
        one at a time to the parsed question list.

        >>> r = Router()
        >>> r.setup(['-f', 'IndexFilter'])
        >>> r.parse(['1. This is the stem'])
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

    def stow(self):
        if self.options.input:
            self.inputs['command_line'] = self.options.input

        if self.options.inputfile == sys.stdin:
            print 'Enter input (ctrl-D on a blank line to end)'
            self.inputs['stdin'] = self.options.inputfile.read()

        else:
            f = self.options.inputfile
            if '.pdf' == f.name [len(f.name)-4:len(f.name)]:
                self.stow_pdf()

            else:
                self.inputs[f.name] = f.read()

    def stow_pdf(self):
        if PdfFileReader:
            contents = []
            pdf = PdfFileReader(file(self.options.inputfile.name))
            if not pdf.isEncrypted:
                for i in range(0, pdf.getNumPages()):
                    page_content = pdf.getPage(i).extractText()
                    if page_content:
                        contents.append(page_content)
                #~ import pdb; pdb.set_trace()
                if not bool([True for x in contents if '\u02dc\u02dc\u02dc\u02dc' in x]): # check if pyPdf had trouble
                    self.inputs['pyPdf'] = contents

        command_line = ['pdftotext', '-raw', self.options.inputfile.name, '-']
        proc = Popen(command_line, stdout=PIPE, stderr=STDOUT)
        out, err = proc.communicate()
        if err:
            self.__error(err)
            raise OSError, 'The program pdftotext was not found in the path.'
        else:
            self.inputs['pdftotext'] = out

    def get_input(self, inputfile=None):
        """
        Return the input from the file designated on the commad line.
        Note that if no input file is designated then the input file
        is the default standard input.

        @param  inputfile  File  The open input file object
        @return  list  The input

        >>> r = Router()
        >>> r.setup(['''This is the stem
        ... This is an option'''])
        >>> print r.get_input()[0]
        This is the stem
        This is an option
        """
        def listify(o):
             return o if type(o) == list else [o]

        if self.options.input:
            # note: any file input is ignored
            return listify(self.options.input)

        inputfile = self.options.inputfile if not inputfile else inputfile

        input = self._read(inputfile)
        #~ import pdb; pdb.set_trace()

        return listify(input)

    # Protected methods
    # ------------------------------------------------------------------

    def _read(self, inputfile):
        """
        A wrapper for inputfile.read() to trap for the PDF conversion
        """
        if '.pdf' == inputfile.name[len(inputfile.name)-4:len(inputfile.name)]:
            return self._get_pdf_contents(inputfile)

        if inputfile == sys.stdin:
            print 'Enter input (ctrl-D on a blank line to end)'

        return inputfile.read()

    def _get_pdf_contents(self, inputfile):
        command_line = ['pdftotext', '-raw', inputfile.name, '-']
        proc = Popen(command_line, stdout=PIPE, stderr=STDOUT)
        out, err = proc.communicate()
        if err:
            self.__error(err)
            raise OSError, 'The program pdftotext was not found in the path.'
        else:
            return out

    def _get_mogrifyers(self):
        for mogrifyer in self.options.mogrifyers:
            try:
                Mogrifyer = self.__forname("mogrifyer", mogrifyer)
            except AttributeError:
                print 'mogrifyer', sys.exc_info()[1]
            else:
                yield Mogrifyer()

    def _get_parser(self, strings=('',)):
        """
        This tries to use some rudimentary intelligence to determine which
        parser to choose based on how many questions it parses out giving
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
        for parserclass in ('IndexParser', 'BlockParser', 'ChunkParser', 'QuestParser', 'StemsParser'):
            Parser = self.__forname("parser", parserclass)
            try:
                q = []
                for string in strings:
                    q.extend(Parser().parse(string).questions)
                questions = Questions(q)
            except OverflowError:
                questions = Questions([])
            self.qhash[parserclass] = questions

        # now look at the parser results to determine which one to use.
        # we first look for an ordered QuestParser and then for an ordered
        # ChunkParser otherwise we look for a symetrical QuestParser and
        # then a symetrical ChunkParser and so on.
        if   False: parser = ''
        elif self.qhash['QuestParser'].length > 1 and self.qhash['QuestParser'].ordered: parser = 'QuestParser'
        elif self.qhash['ChunkParser'].length > 1 and self.qhash['ChunkParser'].ordered: parser = 'ChunkParser'
        elif self.qhash['IndexParser'].length > 1 and self.qhash['IndexParser'].ordered: parser = 'IndexParser'
        elif self.qhash['StemsParser'].length > 1 and self.qhash['StemsParser'].ordered: parser = 'StemsParser'
        elif self.qhash['BlockParser'].length > 1 and self.qhash['BlockParser'].ordered: parser = 'BlockParser'

        elif self.qhash['QuestParser'].length > 1 and self.qhash['QuestParser'].symetrical: parser = 'QuestParser'
        elif self.qhash['ChunkParser'].length > 1 and self.qhash['ChunkParser'].symetrical: parser = 'ChunkParser'
        elif self.qhash['IndexParser'].length > 1 and self.qhash['IndexParser'].symetrical: parser = 'IndexParser'
        elif self.qhash['StemsParser'].length > 1 and self.qhash['StemsParser'].symetrical: parser = 'StemsParser'
        elif self.qhash['BlockParser'].length > 1 and self.qhash['BlockParser'].symetrical: parser = 'BlockParser'

        elif self.qhash['QuestParser'].length > 1: parser = 'QuestParser'
        elif self.qhash['ChunkParser'].length > 1: parser = 'ChunkParser'
        elif self.qhash['IndexParser'].length > 1: parser = 'IndexParser'
        elif self.qhash['StemsParser'].length > 1: parser = 'StemsParser'
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

    def __error(self, errors):
        """
        Writes errors to standard error
        """
        for e in (e for e in errors if e):
            sys.stderr.write(str(e))
            sys.stderr.write(' ')

        sys.stderr.write('\n')
