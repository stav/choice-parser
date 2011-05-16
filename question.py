
class Question(object):
    """
    A question is composed of a stem and a list of options.
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: stem
    # The so-called question
    stem = ''

    # Property: options
    # The list of possible selections
    options = []

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        self.stem = ''
        self.options = []

    def __str__(self):
        return '%s %d' % (self.stem, len(self.options))

class Questions(object):
    """
    A questions is a list of Question objects.
    """

    # Properties
    # ------------------------------------------------------------------

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, questions):
        self.length = len(questions)
        self.symetrical = self.__symetrical(questions)
        self.option_count = self.__get_option_count(questions)

    def __str__(self):
        return self.__repr__

    def __repr__(self):
        return '%d/%d%s' % (self.length, self.option_count, '/*' if self.symetrical else '')

    def __symetrical(self, questions):
        if len(questions) <2: return False
        option_count = None

        for question in questions:
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
