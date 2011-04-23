
import re

from question import Question

class Parser(object):
    """
    The parser looks through the tokens to determine what is the stem and
    what are the options.
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: str
    # The string
    str = ''

    # Property: tokens
    # The list of tokens
    tokens = []

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        self.str = str
        self.tokens  = []
        self._tokenize()

    # Protected methods
    # ------------------------------------------------------------------

    def _tokenize(self):
        """Tokenizes.
        Initializes [[self.tokens]].
        """

        str = self.str.strip()

        # Find prefix/suffix
        #~ while True:
            #~ match = re.match(r"^(\s*<[^>]+>\s*)", str)
            #~ if match is None: break
            #~ if self.prefix is None: self.prefix = ''
            #~ self.prefix += match.group(0)
            #~ str = str[len(match.group(0)):]
#~
        #~ while True:
            #~ match = re.findall(r"(\s*<[^>]+>[\s\n\r]*)$", str)
            #~ if not match: break
            #~ if self.suffix is None: self.suffix = ''
            #~ self.suffix = match[0] + self.suffix
            #~ str = str[:-len(match[0])]

        # Split by the element separators
        for token in re.split('(.*)', str):
            if token.strip() != '':
                self.tokens.append(token)

class SingleParser (Parser):
    """
    The single parser assumes only one question and takes the first line
    to be the stem and the rest are options.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        super(SingleParser, self).__init__(str)

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        """Parses.
        Called by [[Router]].
        """
        if len(self.tokens) == 0: return []

        question = Question()
        question.stem = self.tokens[0]
        question.options = self.tokens[1:] if len(self.tokens) > 1 else []

        return [question]

class IndexParser (Parser):
    """
    The index parser determines stems to be prefixed with numbers and the
    options to be prefixed with letters.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, str):
        super(IndexParser, self).__init__(str)

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        """Parses.
        Called by [[Router]].
        """
        if len(self.tokens) == 0: return []
        
        questions = []
        question = None

        for token in self.tokens:
            print 'token: ', token
            s = re.match(r"\s*\d+\. ", token)
            if s and s.group():
                if question: questions.append(question)
                question = Question()
                question.stem = token.strip()
                
            else:
                try:
                    assert question is not None
                    question.options = self.tokens[1:] if len(self.tokens) > 1 else []

                except AssertionError:
                    pass

        if question: questions.append(question)

        return questions
