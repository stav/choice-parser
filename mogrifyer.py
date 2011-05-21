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
    ... What is the SplitstemMogrifyer?
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

        p = re.compile(r"(\s*[0-9]+\.\s*)$\s+(.*?)$(?=\s*[Aa]\.)", re.MULTILINE | re.DOTALL)
        
        return p.sub('\g<1>\g<2>', string)
        