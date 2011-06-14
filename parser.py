
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser breaks up a string into tokens and then looks through those
    tokens to determine what is the stem and what are the options.
    """
    maxlen = 100000
    
    def __init__(self):
        self._questions  = []
        self._tokens     = []

    def __str__(self):
        return "<%s.%s tokens=%d, questions=%d>" % (
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
        if len(string) > self.maxlen:
            raise OverflowError, 'String of %d bytes is too long, %d max' % (len(string), self.maxlen)

    @property
    def questions(self):
        """
        Read-only attribute for the parsed questions.

        @return  list  The parsed questions
        """
        return self._questions

    @property
    def tokens(self):
        """
        read-only attribute for the tokenized strings.

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
    >>> q = p.questions
    >>> assert len(q) == 1
    >>> assert len(q[0].options) == 2
    """
    def __init__(self):
        super(SingleParser, self).__init__()

    def parse(self, string):
        self._tokenize(string)
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
    >>> i = '''3. What is the name of the part that contains the question?
    ... A.     Multiple
    ... B.     Choice
    ... C.     Problem
    ... D.     Stem
    ... '''
    >>> q = IndexParser().parse(i).questions
    >>> assert len(q) == 1
    >>> assert len(q[0].options) == 4
    """
    def __init__(self):
        super(IndexParser, self).__init__()

    #~ (Pdb) for i in range(len(self.tokens)): print '\n%s %d\n'%('*'*40, i), self.tokens[i]

    def parse(self, string):
        question = None
        import pdb; pdb.set_trace()
        self._tokenize(string)

        for token in self._tokens:
            s = re.match(r"^\s*\d+\.\s", token)
            if s and s.group():
                if question and len(question.options) > 0:
                    self._questions.append(question)
                question = Question()
                question.stem = token
                continue

            if question is not None:
                o = re.match(r"^\s*[a-zA-Z][.):]\s", token)
                if o and o.group():
                    question.options.append(token)

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
    >>> p = BlockParser().parse(i[0])
    >>> len(p.questions)
    11
    """
    def __init__(self):
        super(BlockParser, self).__init__()

    def parse(self, string):
        question = Question()
        option = False

        self._tokenize(string)
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
    >>> q = p.questions
    >>> len(q)
    1
    >>> len(q[0].options)
    4
    """
    def __init__(self):
        super(ChunkParser, self).__init__()
        self._tokenize = self._chunk

    def _chunk(self, string):
        """
        Split input string into tokens based on option groups.  In other
        words we look for a group of lines that start with A, B, C and
        maybe D and E, then assume the stems are the bits between the
        option groups.

        ..note: There is no way to determine when the last option has
        ended in this particular parser which only looks for the option
        sets.  We can't be certain if the the following lines are part
        of the option or part of the next question.  Therefore we cut
        the last option off at the first linefeed, which may, and will
        truncate the last option if it indeed contains linefeeds

        ..note: Also of note is that if there are only four options:
        a, b, c, d - then the fourth option will be only one character
        long since it is using non-greedy dot matching.

        @todo Take the **** at the beginning of an option, to denote the
        correct answer.

        @param  string  The input string
        @return  list  The tokenized input
        """
        #~ a = r'\**\s*(?:a\.?|\(?a\))' #SMA option dot now required
        a = r'\**\s*(?:a\.|\(?a\))'
        b = r'\**\s*(?:b\.|\(?b\))'
        c = r'\**\s*(?:c\.|\(?c\))'
        d = r'\**\s*(?:d\.|\(?d\))'
        e = r'\**\s*(?:e\.|\(?e\))'
        l = r'\s+.+?\s+'
        #                                    last option trucated here \/
        regex = r"({a}{line}{b}{line}{c}{line}(?:{d}{line})(?:{e}.*?)?)\n?".format(
            a=a, b=b, c=c, d=d, e=e, line=l, 
            )
        p = re.compile(regex, re.IGNORECASE | re.DOTALL)

        self._tokens = p.split(string)

    def parse(self, string):
        re_index  = r'\**\s*(?:[A-Ea-e]\.|\(?[A-Ea-e]\))'
        re_body   = r'.+'
        re_option = r'({index}\s+{body})'.format(index=re_index, body=re_body)
        self._tokenize(string)

        # spin thru the input chunks two at a time, the first being the
        # stem, presumably, and the second being the option group
        for st_index in range(0, len(self._tokens), 2):
            op_index = st_index +1
            if op_index < len(self._tokens):
                question = Question()

                stem = re.search(r'[0-9]+(?:\.|\s).+$', self._tokens[st_index], re.DOTALL)
                #~ stem = re.search(r"\n*((?:[0-9]*\.*\s*).+)$", self._tokens[st_index], re.DOTALL)
                #~ stem = re.search(r"(?:[0-9]+\s+(?:.|\n)+$)+?|(?:\n*.+$)", self._tokens[st_index])
                question.stem = stem.group().strip() if stem else self._tokens[st_index] 

                options = [o.strip() for o in re.split(re_option, self._tokens[op_index]) if o.strip()]
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
    >>> q = p.questions
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
        self._tokenize = self._quest

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

        self._tokens = p.split(string) # re.IGNORECASE doesn't really work unless you re.compile it

    def parse(self, string):
        super(QuestParser, self).parse(string)
        regex = self._format(r"({i}{w}{body})({a}{w}{body})({b}{w}{body})({c}{w}{body})({d}{w}{body})?({e}{w}{body})?{lb}")

        self._tokenize(string)
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
    >>> q = p.questions
    >>> assert len(q) == 1
    >>> assert len(q[0].options) == 3
    """
    def __init__(self):
        super(StemsParser, self).__init__()
        self._tokenize = self._stemify

    def parse(self, string):
        super(StemsParser, self).parse(string)
        si = r'[0-9]+\.\s+'
        sb = r'.+?[?:.]\n\n'
        o  = r'.+'
        regex = r"({si}{sb})({o})".format(
            si=si, sb=sb, o=o,
            )

        self._tokenize(string)
        for token in self._tokens:
            question = Question()
            match = re.search(regex, token, re.DOTALL)
            if match:
                question.stem = match.group(1).strip()
                for option in match.group(2).split('\n'):
                    if option:
                        question.options.append(option.strip())
                    else:
                        break
                self._questions.append(question)

        return self
