
import re

class Parser:
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
        print 'Parser __init__() tokens: ', self.tokens

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

    # Public methods
    # ------------------------------------------------------------------

    def parse(self):
        """Parses.
        Called by [[Router]].
        """
        if len(self.tokens) == 0: return

        options_cnt = len(self.tokens) - 1
        output = "stem: %s\n" % self.tokens[0]

        for o in self.tokens[1:]:
            output += "option: %s\n" % o

        output += 'stats: stem is %d bytes long, %d option%s found\n' % (
            len(self.tokens[0]),
            options_cnt,
            's' if options_cnt != 1 else ''
            )

        return output
