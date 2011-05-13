"""
Mogrification takes the input string and does some massaging and then returns
the results.
"""
import re

########################################################################
class BooleanoptionMogrifyer (object):
    """
    The boolean option mogrify removes any 'Yes' or 'No' that precedes
    any options.

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
