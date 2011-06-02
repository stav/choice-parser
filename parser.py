
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser breaks up a string into tokens and then looks through those
    tokens to determine what is the stem and what are the options.
    """
    def __init__(self):
        self._get_tokens = self._tokenize
        self._questions  = []
        self._tokens     = []

    def __str__(self):
        return '<%s.%s tokens=%d, questions=%d>' % (
            __name__,
            self.__class__.__name__,
            len(self._tokens),
            len(self._questions),
            )

    def _tokenize(self, string):
        """
        Split input string into tokens based on line-breaks.

        @param  string  The input string
        @return  list  The tokenized input
        """
        self._tokens = []

        # Split and strip the input string by newlines
        for token in re.split('(.*)', string):
            if token.strip() != '':
                self._tokens.append(token)

    def _chunk(self, string):
        """
        Split input string into tokens based on option groups.  In other
        words we look for a group of lines that start with A, B, C and
        maybe D and then assume the stem is the bit before each.

        @param  string  The input string
        @return  list  The tokenized input
        """
        a = '(?:a\.?|\(?a\))'
        b = '(?:b\.?|\(?b\))'
        c = '(?:c\.?|\(?c\))'
        d = '(?:d\.?|\(?d\))'
        e = '(?:e\.?|\(?e\))'
        l = '.*\s*'
        s = '\s+'
        regex = r"(\s*{a}{s}{line}{b}{s}{line}{c}{s}{line}(?:{d}{s}{line})(?:{e}.*)?)".format(
            a=a, b=b, c=c, d=d, e=e, line=l, s=s
            )
        p = re.compile(regex, re.IGNORECASE)

        self._tokens = p.split(string)

    def _stemify(self, string):
        """
        Look for the stems and everything in between must be the options.

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

        self._tokens = [t.strip() for t in p.split(string) if t]

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
    def __init__(self):
        super(SingleParser, self).__init__()

    def parse(self, string):
        self._get_tokens(string)
        if not self._tokens: return self

        question = Question()
        question.stem = self._tokens[0]
        question.options = self._tokens[1:] if len(self._tokens) > 1 else []

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
    def __init__(self):
        super(IndexParser, self).__init__()

    def parse(self, string):
        question = None
        self._get_tokens(string)
        for token in self._tokens:
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
    def __init__(self):
        super(BlockParser, self).__init__()

    def parse(self, string):
        question = Question()
        option = False

        self._get_tokens(string)
        for token in self._tokens:
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
    def __init__(self):
        super(ChunkParser, self).__init__()
        self._get_tokens = self._chunk

    def parse(self, string):
        re_index  = r'(?:[A-Za-z]\.?|\(?[A-Za-z]\))'
        re_body   = r'.+'
        re_option = r'(\n+{index}\s+{body}\s*)'.format(index=re_index, body=re_body)
        self._get_tokens(string)

        # spin thru the input chunks two at a time, the first being the
        # stem, presumably, and the second being the option group
        for st_index in range(0, len(self._tokens), 2):
            op_index = st_index +1
            question = Question()
            stem = re.search(r"\n*(.+)$", self._tokens[st_index])
            if stem:
                question.stem = stem.group().strip()

                if op_index < len(self._tokens):
                    options = [o.strip() for o in re.split(re_option, self._tokens[op_index]) if o]
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
    stem_index = r'[0-9.]+(?:\.|\))'
    option_a   = r'A(?::|\))'
    option_b   = r'B(?::|\))'
    option_c   = r'C(?::|\))'
    option_d   = r'D(?::|\))'
    option_e   = r'E(?::|\))'
    body       = r'.+?'
    whitespace = r'\s+'
    double_line_break = r'(?:(\n\n)|(\s*$))'

    def __init__(self):
        super(QuestParser, self).__init__()
        self._get_tokens = self._quest

    def _format(self, regex):
        return regex.format(
            i    =self.stem_index,
            a    =self.option_a,
            b    =self.option_b,
            c    =self.option_c,
            d    =self.option_d,
            e    =self.option_e,
            body =self.body,
            w    =self.whitespace,
            lb   =self.double_line_break,
            )

    def _quest(self, string):
        """
        Create one token for each question, including the stem and the
        options in the token.

        @param  string  The input string
        @return  list  The tokenized input
        """
        regex = self._format(r"({i}{w}{body}{a}{w}{body}{b}{w}{body}{c}{w}{body}(?:{d}{w}{body})?(?:{e}{w}{body})?(?={i}{w}))")
        p = re.compile(regex, re.DOTALL | re.IGNORECASE)

        self._tokens = p.split(string) # re.IGNORECASE doesn't really work unless you re.compiles it

        #~ if self._tokens is None: self._tokens = []

    def parse(self, string):
        regex = self._format(r"({i}{w}{body})({a}{w}{body})({b}{w}{body})({c}{w}{body})({d}{w}{body})?({e}{w}{body})?{lb}")

        self._get_tokens(string)
        for token in [t.strip() for t in self._tokens if t]:
            question = Question()
            match = re.search(regex, token, re.DOTALL | re.IGNORECASE)
            if match:
                question.stem = match.group(1).strip()
                question.options.append(match.group(2).strip())
                question.options.append(match.group(3).strip())
                question.options.append(match.group(4).strip())
                if match.group(5): question.options.append(match.group(5).strip())
                if match.group(6): question.options.append(match.group(6).strip())
                self._questions.append(question)

        return self

########################################################################
class StemsParser (Parser):
    """
    The stems parser uses the _stemify() tokenizer.

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
    def __init__(self):
        super(StemsParser, self).__init__()
        self._get_tokens = self._stemify

    def parse(self, string):
        si = r'[0-9]+\.\s+'
        sb = r'.+?[?:.]\n\n'
        o  = r'.+'
        regex = r"({si}{sb})({o})".format(
            si=si, sb=sb, o=o,
            )

        #import pdb; pdb.set_trace()
        self._get_tokens(string)
        for token in self._tokens:
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
