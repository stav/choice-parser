
import re

from router import Question

########################################################################
class IndexFilter (object):
    """
    The index filter peels off the numbering.
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
    """
    def filter(self, questions):
        filtered_questions = []

        for question in questions:
            q = Question()
            q.stem = question.stem.strip()

            for option in question.options:
                q.options.append(option.strip())

            filtered_questions.append(q)

        return filtered_questions

########################################################################
class QualifiedFilter (object):
    """
    The qualified filter prints out the field descriptions.
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
