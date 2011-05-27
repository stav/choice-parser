
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser breaks up a string into tokens and then looks through those
    tokens to determine what is the stem and what are the options.
    """
    def __init__(self, safety=False):
        self._get_tokens = self._tokenize
        self._safety     = safety
        self._questions  = []
        self._tokens     = []

    def __str__(self):
        return '<%s.%s save=%s, tokens=%d, questions=%d>' % (
            __name__,
            self.__class__.__name__,
            self._safety,
            len(self._tokens),
            len(self._questions),
            )

    def __safety(self, tokens):
        if self._safety:
            self._tokens = tokens
        return tokens

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

        return self.__safety(tokens)

    def _chunk(self, string):
        """
        Split input string into tokens based on option groups.  In other
        words we look for a group of lines that start with A, B, C and
        maybe D and then assume the stem is the bit before each.

        @param  string  The input string
        @return  list  The tokenized input
        """
        a = '(?:A\.?|\(A\))'
        b = '(?:B\.?|\(B\))'
        c = '(?:C\.?|\(C\))'
        d = '(?:D\.?|\(D\))'
        e = '(?:E\.?|\(E\))'
        l = '[^\n\r]*\n\s*'
        s = '\s+'
        regex = r"(\s*{a}{s}{line}{b}{s}{line}{c}{s}{line}(?:{d}{s}{line})(?:{e}.*)?)".format(
            a=a, b=b, c=c, d=d, e=e, line=l, s=s
            )
        p = re.compile(regex, re.IGNORECASE)

        return self.__safety(p.split(string))

    def _quest(self, string):
        """
        Create one token for each question, including the options in the token.

        @param  string  The input string
        @return  list  The tokenized input
        """
        si = r'[0-9]+\.'
        oa = r'A:'
        ob = r'B:'
        oc = r'C:'
        od = r'D:'
        body = r'.+?'
        s = '\s+'
        regex = r"({i}{s}{body}{a}{s}{body}{b}{s}{body}{c}{s}{body}{d}{s}{body}(?={i}{s}))".format(
            i=si, a=oa, b=ob, c=oc, d=od, body=body, s=s
            )
        p = re.compile(regex, re.DOTALL)

        return self.__safety([t.strip() for t in p.split(string) if t])

    def _stemify(self, string):
        """
        Create one token for each question, including the options in the token.

        @param  string  The input string
        @return  list  The tokenized input
        """
        si = r'\n\n[0-9]+\.\s+'
        sb = r'.+?[?:.]\n\n'
        o  = r'.+?'
        regex = r"({si}{sb}{o}(?={si}))".format(
            si=si, sb=sb, o=o,
            )
        p = re.compile(regex, re.DOTALL)

        return self.__safety([t.strip() for t in p.split(string) if t])

    def parse(self, string):
        """
        Spin thru the tokens and create a list of Questions.

        @param  string  The input string to parse
        @return  Parser  Enable method chaining
        """
        pass

    def get_questions(self):
        """
        Return the parsed questions list.

        @return  list  The parsed questions
        """
        return self._questions

    def get_tokens(self):
        """
        Return the tokenized string list

        @return  list  The tokens
        """
        return self._tokens

########################################################################
class SingleParser (Parser):
    """
    The single parser assumes only one question and takes the first token
    to be the stem and the rest of the tokens are the options.

    >>> from parser import SingleParser
    >>> i = '''This is the stem
    ... This is the first option
    ... This is the second option
    ... '''
    >>> p = SingleParser().parse(i)
    >>> q = p.get_questions()
    >>> assert len(q) == 1
    >>> assert len(q[0].options) == 2
    """
    def __init__(self, safety=False):
        super(SingleParser, self).__init__(safety)

    def parse(self, string):
        tokens = self._get_tokens(string)
        if not tokens: return self

        question = Question()
        question.stem = tokens[0]
        question.options = tokens[1:] if len(tokens) > 1 else []

        self._questions.append(question)

        return self

########################################################################
class IndexParser (Parser):
    """
    The index parser determines stems to be prefixed with numbers and the
    options to be prefixed with letters.

    >>> from router import Router
    >>> r = Router()
    >>> r.setup(['-i', 'input/anarchy'])
    >>> i = r.get_input()
    >>> p = IndexParser().parse(i)
    >>> len(p.get_questions())
    10
    """
    def __init__(self, safety=False):
        super(IndexParser, self).__init__(safety)

    def parse(self, string):
        question = None
        for token in self._get_tokens(string):
            s = re.match(r"^\s*\d+\.\s", token)
            if s and s.group():
                if question and len(question.options) > 0:
                    self._questions.append(question)
                question = Question()
                question.stem = token
                continue

            o = re.match(r"^\s*[a-zA-Z][.):]\s", token)
            if o and o.group():
                try:
                    assert question is not None
                    question.options.append(token)

                except AssertionError:
                    pass

        if question and len(question.options) > 0:
            self._questions.append(question)

        return self

########################################################################
class BlockParser (Parser):
    """
    The block parser determines stems to be all the text in between the
    options.

    >>> from router import Router
    >>> r = Router()
    >>> r.setup(['-i', 'input/drivers'])
    >>> i = r.get_input()
    >>> p = BlockParser().parse(i)
    >>> len(p.get_questions())
    11
    """
    def __init__(self, safety=False):
        super(BlockParser, self).__init__(safety)

    def parse(self, string):
        question = Question()
        option = False

        for token in self._get_tokens(string):
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
                self._questions.append(question)
                question = Question()
                question.stem = ''
                option = False

            try:
                assert question is not None
                question.stem += token + '\n'
            except AssertionError:
                pass

        if question and len(question.options) > 0:
            self._questions.append(question)

        return self

########################################################################
class ChunkParser (Parser):
    """
    The chunnk parser does not tokenize by lines but instead by groups of
    lines separated by the option list; therefore, every other entry in
    the split list consists of, theoretically, the stem followed by the
    option list in the following entry which then is split line by line
    for the individual options.

    >>> from router import Router
    >>> r = Router()
    >>> i = '''3. What is the name of the part that contains the question?
    ... A.     Multiple
    ... B.     Choice
    ... C.     Problem
    ... D.     Stem
    ... '''
    >>> p = ChunkParser().parse(i)
    >>> q = p.get_questions()
    >>> len(q)
    1
    >>> len(q[0].options)
    4
    """
    def __init__(self, safety=False):
        super(ChunkParser, self).__init__(safety)
        self._get_tokens = self._chunk

    def parse(self, string):
        re_index  = r'(?:[A-Za-z]\.?|\([A-Za-z]\))'
        re_body   = r'[^\n]+'
        re_option = r'(\s*{index}\s+{body}\s*)'.format(index=re_index, body=re_body)
        chunks = self._get_tokens(string)

        # spin thru the input chunks two at a time, the first being the
        # stem, presumably, and the second being the option group
        for st_index in range(0, len(chunks), 2):
            op_index = st_index +1
            question = Question()
            stem = re.search(r"\n*(.+)$", chunks[st_index])
            if stem:
                question.stem = stem.group().strip()

                if op_index < len(chunks):
                    options = [o.strip() for o in re.split(re_option, chunks[op_index]) if o]
                    #import pdb; pdb.set_trace()
                    for option in options:
                        question.options.append(option)

                    self._questions.append(question)

        return self

########################################################################
class QuestParser (Parser):
    """
    The quest parser uses the _quest() tokenizer.

    >>> from router import Router
    >>> r = Router()
    >>> i = '''6. The bacteria Staphylococcus
    ... aureus can be classified as a:A: Gram-negative cocciB: Spirochetes
    ... C: Acid-fast bacilli D: Gram-positive cocci
    ... '''
    >>> p = QuestParser().parse(i)
    >>> q = p.get_questions()
    >>> len(q)
    1
    >>> len(q[0].options)
    4
    """
    def __init__(self, safety=False):
        super(QuestParser, self).__init__(safety)
        self._get_tokens = self._quest

    def parse(self, string):
        si = r'[0-9]+\.'
        oa = r'A:'
        ob = r'B:'
        oc = r'C:'
        od = r'D:'
        body = r'.+?'
        double_line_break = r'(?:(\n\n)|(\s*$))'
        s = '\s+'
        regex = r"({i}{s}{body})({a}{s}{body})({b}{s}{body})({c}{s}{body})({d}{s}.*?){lb}".format(
            i=si, a=oa, b=ob, c=oc, d=od, body=body, s=s, lb=double_line_break,
            )

        for token in self._get_tokens(string):
            question = Question()
            match = re.search(regex, token, re.DOTALL)
            #if match: print match.group(); import pdb; pdb.set_trace()
            if match:
                question.stem = match.group(1).strip()
                question.options.append(match.group(2).strip())
                question.options.append(match.group(3).strip())
                question.options.append(match.group(4).strip())
                question.options.append(match.group(5).strip())
                self._questions.append(question)

        return self

########################################################################
class StemsParser (Parser):
    """
    The quest parser uses the _quest() tokenizer.

    >>> from router import Router
    >>> r = Router()
    >>> i = '''2. Grabbing the front brake or jamming down on the rear brake:
    ...
    ... Can cause the brakes to lock.
    ... Is the best way to stop in an emergency.
    ... Is the best way to slow down when the streets are wet.
    ... '''
    >>> p = StemsParser().parse(i)
    >>> q = p.get_questions()
    >>> assert len(q) == 1
    >>> assert len(q[0].options) == 3
    """
    def __init__(self, safety=False):
        super(StemsParser, self).__init__(safety)
        self._get_tokens = self._stemify

    def parse(self, string):
        si = r'[0-9]+\.\s+'
        sb = r'.+?[?:.]\n\n'
        o  = r'.+'
        regex = r"({si}{sb})({o})".format(
            si=si, sb=sb, o=o,
            )

        #import pdb; pdb.set_trace()
        for token in self._get_tokens(string):
            question = Question()
            match = re.search(regex, token, re.DOTALL)
            #if match: print match.group(); import pdb; pdb.set_trace()
            if match:
                question.stem = match.group(1).strip()
                for option in match.group(2).split('\n'):
                    if option:
                        question.options.append(option.strip())
                    else:
                        break
                self._questions.append(question)

        return self
