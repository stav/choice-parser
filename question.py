
import re

class Question(object):
    """
    A question is composed of a stem and a list of options.
    """
    def __init__(self):
        self.stem = ''
        self.options = []

    def __str__(self):
        return '%-72s %4d byte stem,%2d options' % (self.stem[0:72], len(self.stem), len(self.options))

    def is_valid(self):
        count = len(self.options)
        return True if count > 1 and count < 11 else False

class Questions(object):
    """
    A Questions is a list of Question objects.

    A lightweight property container that gives information about a list
    of questions but this object does not store the actual question data.
    """
    def __init__(self, questions):
        self.length = len(questions)
        self.symetrical = self.__symetrical(questions)
        self.option_count = self.__get_option_count(questions)
        self.ordered = self.__is_ordered(questions)

    def __str__(self):
        return self.__repr__

    def __repr__(self):
        return '%d/%d/%s/%s' % (self.length, self.option_count, 'o' if self.ordered else '', 's' if self.symetrical else '')

    def __symetrical(self, questions):
        if len(questions) <2: return False
        option_count = None

        for question in questions:
            if not question.is_valid(): return False
            if option_count is None:
                option_count = len(question.options)
            else:
                if len(question.options) != option_count:
                    return False
        return True

    def __get_option_count(self, questions):
        option_count = 0

        for question in questions:
            option_count += len(question.options)

        return option_count

    def __is_ordered(self, questions):
        if len(questions) <2: return False

        for i in range(0, len(questions)):
            if not questions[i].is_valid(): return False
            index_match = re.search(r'^\s*([0-9]+)', questions[i].stem)
            if not index_match: return False

            index = int(index_match.group(1))
            if index != i+1: return False

        return True
