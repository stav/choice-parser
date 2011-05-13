
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser looks through the tokens to determine what is the stem and
    what are the options.
    """
    def __init__(self):
        self.tokens  = []

    def _tokenize(self, string):
        """
        Each Parser subclass in this module, by deafult, first splits up 
        the input into tokens.  Then it spins thru the tokens and creates 
        a list of question objects for each stem found, adds in the options 
        and returns the whole list to the router.

        ..note: Currently the tokenizing is based on line-breaks.
        """
        # combine stem spilt into lines into a single line:
        #     1.
        #     What is a disadvantage of multiple-choice questions?
        #       A.     Time needed to score them
        # becomes:
        #     1. What is a disadvantage of multiple-choice questions?
        #       A.     Time needed to score them
        p = re.compile(r"(\s*[12]+\.\s*)$\s+(.*?)$(?=\s*[Aa]\.)", re.MULTILINE | re.DOTALL)
        string = p.sub('\g<1>\g<2>', string)

        # Split and strip the input string by newlines
        for token in re.split('(.*)', string):
            if token.strip() != '':
                self.tokens.append(token)
                
        return len(self.tokens)

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
    >>> p = SingleParser()
    >>> q = p.parse(i)[0]
    >>> len(q.options)
    2
    """
    def __init__(self):
        super(SingleParser, self).__init__()

    def parse(self, string):
        if not self._tokenize(string): return []

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
    >>> p = IndexParser()
    >>> Q = p.parse(i)
    >>> len(Q)
    10
    """
    def __init__(self):
        super(IndexParser, self).__init__()

    def parse(self, string):
        if not self._tokenize(string): return []

        questions = []
        question = None
        #~ import pdb; pdb.set_trace()

        for token in self.tokens:
            #~ print 'token: ', token
            s = re.match(r"^\s*\d+\.\s", token)
            if s and s.group():
                if question and len(question.options) > 0: 
                    questions.append(question)
                question = Question()
                question.stem = token
                continue

            o = re.match(r"^\s*[a-zA-Z][.)]\s", token)
            if o and o.group():
                try:
                    assert question is not None
                    question.options.append(token)

                except AssertionError:
                    pass

        if question and len(question.options) > 0: 
            questions.append(question)

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
    >>> p = BlockParser()
    >>> Q = p.parse(i)
    >>> len(Q)
    11
    """
    def __init__(self):
        super(BlockParser, self).__init__()

    def parse(self, string):
        if not self._tokenize(string): return []

        questions = []
        question = Question()
        option = False

        for token in self.tokens:
            #~ print 'token: ', token
            o = re.match(r"^\s*[a-zA-Z][.)] ", token)
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

        if question and len(question.options) > 0: 
            questions.append(question)

        return questions
