
import re

from router import Question

########################################################################
class IndexFilter (object):
    """
    The index filter peels off the numbering.

    >>> from question import Question
    >>> q = Question()
    >>> q.stem = '1. What is the IndexFilter?'
    >>> q.options.append('a. A choice-parser component.')
    >>> q.options.append('b. A Filter class.')
    >>> q.options.append('c. Both of the above.')
    >>> len(q.stem)
    27
    >>> f = IndexFilter()
    >>> q = f.filter([q])[0]
    >>> len(q.stem)
    25
    >>> len(q.options)
    3
    """
    def filter(self, questions):
        filtered_questions = []

        for question in questions:
            q = Question()

            match = re.match(r"^[0-9]*\.?(.*)$", question.stem)
            if match:
                q.stem = match.group(1)
            else:
                q.stem = question.stem

            for option in question.options:
                q.options.append(option)

            filtered_questions.append(q)

        return filtered_questions

########################################################################
class WhitespaceFilter (object):
    """
    The white-space filter strips off white-space.

    >>> from question import Question
    >>> q = Question()
    >>> q.stem = ' 	 	 1. What is the WhitespaceFilter? 	 	 '
    >>> q.options.append('	a. A choice-parser component.')
    >>> q.options.append('	b. A Filter class.')
    >>> q.options.append('	c. Both of the above.')
    >>> len(q.stem)
    63
    >>> f = WhitespaceFilter()
    >>> q = f.filter([q])[0]
    >>> len(q.stem)
    32
    >>> len(q.options)
    3
    """
    def filter(self, questions):
        filtered_questions = []

        for question in questions:
            q = Question()
            q.stem = re.sub(r"\s+", ' ', question.stem).strip()

            for option in question.options:
                q.options.append(re.sub(r"\s+", ' ', option).strip())

            filtered_questions.append(q)

        return filtered_questions

########################################################################
class QualifiedFilter (object):
    """
    The qualified filter prints out the field descriptions.

    >>> from question import Question
    >>> q = Question()
    >>> q.stem = '1. What is the QualifiedFilter?'
    >>> q.options.append('a. A choice-parser component.')
    >>> q.options.append('b. A Filter class.')
    >>> q.options.append('c. Both of the above.')
    >>> len(q.stem)
    31
    >>> f = QualifiedFilter()
    >>> q = f.filter([q])[0]
    >>> len(q.stem)
    38
    >>> len(q.options)
    3
    """
    def filter(self, questions):
        filtered_questions = []

        for question in questions:
            q = Question()
            q.stem = 'stem = %s' % question.stem

            for option in question.options:
                q.options.append('option = %s' % option)

            filtered_questions.append(q)

        return filtered_questions
