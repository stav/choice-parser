
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser looks through the tokens to determine what is the stem and
    what are the options.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        self.str = str
        self.tokens  = []
        self._tokenize()

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        """
        Spins thru the tokens and creates a list of question objects for
        each stem found, adds in the options and returns the whole list
        to the router.
        """
        pass

    # Protected methods
    # ------------------------------------------------------------------

    def _tokenize(self):
        """
        Each class in this parser module, by deafult, first splits up the 
        intput into tokens.  
        
        ..note: Currently the tokenizing is based on line-breaks.
        """
        # Find prefix/suffix
        #~ while True:
            #~ match = re.match(r"^(\s*<[^>]+>\s*)", str)
            #~ if match is None: break
            #~ if self.prefix is None: self.prefix = ''
            #~ self.prefix += match.group(0)
            #~ str = str[len(match.group(0)):]
        #~ while True:
            #~ match = re.findall(r"(\s*<[^>]+>[\s\n\r]*)$", str)
            #~ if not match: break
            #~ if self.suffix is None: self.suffix = ''
            #~ self.suffix = match[0] + self.suffix
            #~ str = str[:-len(match[0])]

        # Split the input string by newlines
        for token in re.split('(.*)', self.str):
            if token.strip() != '':
                self.tokens.append(token)

########################################################################
class SingleParser (Parser):
    """
    The single parser assumes only one question and takes the first line
    to be the stem and the rest of the lines are the options.

    >>> from parser import SingleParser
    >>> i = '''This is the stem
    ... This is the first option
    ... This is the second option
    ... '''
    >>> p = SingleParser(i)
    >>> q = p.parse()[0]
    >>> len(q.options)
    2
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        super(SingleParser, self).__init__(str)

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        if len(self.tokens) == 0: return []

        question = Question()
        question.stem = self.tokens[0]
        question.options = self.tokens[1:] if len(self.tokens) > 1 else []

        return [question]

########################################################################
class IndexParser (Parser):
    """
    The index parser determines stems to be prefixed with numbers and the
    options to be prefixed with letters.

    >>> from router import Router
    >>> from parser import IndexParser
    >>> r = Router()
    >>> i = r.get_input('input/anarchy')
    >>> p = IndexParser(i)
    >>> Q = p.parse()
    >>> len(Q)
    10
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        super(IndexParser, self).__init__(str)

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        if len(self.tokens) == 0: return []

        questions = []
        question = None
        #~ import pdb; pdb.set_trace()

        for token in self.tokens:
            #~ print 'token: ', token
            s = re.match(r"^\s*\d+\. ", token)
            if s and s.group():
                if question: questions.append(question)
                question = Question()
                question.stem = token
                continue

            o = re.match(r"^\s*[a-zA-Z]+[.)] ", token)
            if o and o.group():
                try:
                    assert question is not None
                    question.options.append(token)

                except AssertionError:
                    pass

        if question: questions.append(question)

        return questions

########################################################################
class BlockParser (Parser):
    """
    The block parser determines stems to be all the text in between the
    options.

    >>> from router import Router
    >>> from parser import BlockParser
    >>> r = Router()
    >>> i = r.get_input('input/drivers')
    >>> p = BlockParser(i)
    >>> Q = p.parse()
    >>> len(Q)
    12
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        super(BlockParser, self).__init__(str)

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        if len(self.tokens) == 0: return []

        questions = []
        question = Question()
        option = False

        for token in self.tokens:
            #~ print 'token: ', token
            o = re.match(r"^\s*[a-zA-Z]+[.)] ", token)
            if o and o.group():
                option = True
                try:
                    assert question is not None
                    question.options.append(token)
                except AssertionError:
                    pass
                continue

            if option:
                questions.append(question)
                question = Question()
                question.stem = ''
                option = False

            try:
                assert question is not None
                question.stem += token + '\n'
            except AssertionError:
                pass

        if question: questions.append(question)

        return questions
