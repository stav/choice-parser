
import re

from router import Question

########################################################################
class IndexFilter (object):
    """
    The white-space filter strips off white-space.
    """
    def filter(self, questions):
        filtered_questions = []

        for question in questions:
            q = Question()

            match = re.match(r"^\s*[0-9]*\.?\s*(.*)$", question.stem)
            if match:
                q.stem = match.group(1).strip()
            else:
                q.stem = question.stem.strip()

            for option in question.options:
                q.options.append(option.strip())

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
