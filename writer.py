
########################################################################
class Writer(object):
    """
    The writer outputs the questions.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        pass

    # Public methods
    # ------------------------------------------------------------------

    def write(self):
        pass

########################################################################
class TextWriter (Writer):
    """
    The text writer just attempts to write the questions out in the same
    basic, tho not nessisarily identical, format.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        super(TextWriter, self).__init__()

    # Public methods
    # ------------------------------------------------------------------

    def write(self, output, questions):
        super(TextWriter, self).write()

        for question in questions:
            output.writelines((question.stem, '\n'))

            for option in question.options:
                output.writelines((option, '\n'))

            output.write('\n')
