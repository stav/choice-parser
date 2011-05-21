
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser breaks up a string into tokens and then looks through those 
    tokens to determine what is the stem and what are the options.
    """
    def __init__(self):
        pass

    def _tokenize(self, string):
        """
        Split input string into tokens based on line-breaks.
        
        @param  string  The input string
        @return  list  The tokenized input
        """
        tokens = []

        # Split and strip the input string by newlines
        for token in re.split('(.*)', string):
            if token.strip() != '':
                tokens.append(token)

        return tokens

    def _chunk(self, string):
        """
        Split input string into tokens based on option groups.  In other
        words we look for a group of lines that start with A, B, C and 
        maybe D and then assume the stem is the bit before each.
        
        @param  string  The input string
        @return  list  The tokenized input
        """
        #                    A .          $   B .          $   C .          $      D .          $
        p = re.compile(r"(\s*A\.\s+[^\n]+\n\s*B\.\s+[^\n]+\n\s*C\.\s+[^\n]+\n\s*(?:D\.\s+[^\n]+\n\s*)?)")
        return p.split(string)

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
        tokens = self._tokenize(string)
        if not tokens: return []

        question = Question()
        question.stem = tokens[0]
        question.options = tokens[1:] if len(tokens) > 1 else []

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
        questions = []
        question = None

        for token in self._tokenize(string):
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
        questions = []
        question = Question()
        option = False

        for token in self._tokenize(string):
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

########################################################################
class ChunkParser (Parser):
    def __init__(self):
        super(ChunkParser, self).__init__()

    def parse(self, string):
        questions = []
        question = None
        chunks = self._chunk(string)

        #import pdb; pdb.set_trace()
        # spin thru the input chunks two at a time, the first being the
        # stem, presumably, and the second being the option group
        for index in range(0, len(chunks), 2):
            question = Question()
            question.stem = chunks[index]

            if index+1 < len(chunks):
                for option in [m.strip() for m in re.split(r"(\s*[A-D]\.\s+[^\n]+\s*)", chunks[index+1]) if m]:
                    question.options.append(option)

                questions.append(question)

        return questions
