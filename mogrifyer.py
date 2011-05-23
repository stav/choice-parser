"""
Mogrification takes the input string and does some massaging and then returns
the results.
"""
import re

########################################################################
class BooleanoptionMogrifyer (object):
    """
    The boolean option mogrifier removes any 'Yes' or 'No' that precedes
    the options.

    >>> q = '''1. What is the BooleanoptionMogrifyer?
    ...   Yes  No  a. A choice-parser component.
    ...   Yes  No  b. A Mogrifyer class.
    ...   Yes  No  c. Both of the above.
    ... '''
    >>> m = BooleanoptionMogrifyer()
    >>> print m.mogrify(q)
    1. What is the BooleanoptionMogrifyer?
      a. A choice-parser component.
      b. A Mogrifyer class.
      c. Both of the above.
    """
    def mogrify(self, string):

        p = re.compile(r"^(\s*yes\s+no(?=\s+[a-z]\.))", re.IGNORECASE | re.MULTILINE)

        return p.sub('', string)

########################################################################
class SplitstemMogrifyer (object):
    """
    The split-stem mogrifier joins stems that have a line-break directly
    after the stem's index.

    this::
        1.
        What is a disadvantage of multiple-choice questions?
        A.     Time needed to score them

    becomes::
        1. What is a disadvantage of multiple-choice questions?
        A.     Time needed to score them

    >>> q = '''1.
    ... What is the
    ... SplitstemMogrifyer?
    ...   a. A choice-parser component.
    ...   b. A Mogrifyer class.
    ...   c. Both of the above.
    ... '''
    >>> m = SplitstemMogrifyer()
    >>> print m.mogrify(q)
    1. What is the SplitstemMogrifyer?
      a. A choice-parser component.
      b. A Mogrifyer class.
      c. Both of the above.
    """
    def mogrify(self, string):

        stem_index               = r'\n\s*[0-9]+\.'           #  \n1.
        stem_body                = r'.*?'                     #  What is the SplitstemMogrifyer? (nongreedy)
        option_index_with_dot    = r'(\n\s*\(?[Aa](?:\.|\)))' #  \n A. | A) | (A)  (match group 2)
        option_index_without_dot = r'(:\s*\n\s*[Aa])'         # :\nA  (match group 3)

        regex = r"({si}{sb})(?:{a1}|{a2})".format(
            si =stem_index,
            sb =stem_body,
            a1 =option_index_with_dot,
            a2 =option_index_without_dot,
            )
        re_stem = re.compile(regex, re.MULTILINE | re.DOTALL)

        a =    r'(\(?[Aa](?:\.|\))\s*.*?\n)'
        b =    r'(\(?[Bb](?:\.|\))\s*.*?\n)'
        c =    r'(\(?[Cc](?:\.|\))\s*.*?\n)'
        d = r'((?:\(?[Dd](?:\.|\))\s*.*?\n)?)'
        e = r'((?:\(?[Ee](?:\.|\))\s*.*?\n)?)'

        regex = r"{a}{b}{c}{d}{e}".format(
            a=a,
            b=b,
            c=c,
            d=d,
            e=e,
            )
        re_options = re.compile(regex, re.MULTILINE | re.DOTALL)

        mogrified_string = re_stem   .sub(self.__yank_newlines_from_stem, string, 0)
        mogrified_string = re_options.sub(self.__yank_newlines_from_options, mogrified_string, 0)

        return mogrified_string

    def __yank_newlines_from_stem(self, match):

        m1 = match.group(1).replace('\n', ' ')
        m2 = match.group(2) if match.group(2) else ''
        m3 = match.group(3) if match.group(3) else ''

        ret = '\n%s%s%s' % (m1, m2, m3)
        #print ret; import pdb; pdb.set_trace()
        return ret

    def __yank_newlines_from_options(self, match):

        m1 = match.group(1).replace('\n', ' ').strip() + '\n'
        m2 = match.group(2).replace('\n', ' ').strip() + '\n'
        m3 = match.group(3).replace('\n', ' ').strip() + '\n'
        m4 = match.group(4).replace('\n', ' ').strip() + '\n'
        m5 = match.group(5).replace('\n', ' ').strip() + '\n'

        ret = '%s%s%s%s%s' % (m1, m2, m3, m4, m5)
        #print ret; import pdb; pdb.set_trace()
        return ret
