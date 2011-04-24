
class Question:
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
