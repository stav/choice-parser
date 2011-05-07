
import json
from router import Question

########################################################################
class Writer(object):
    """
    The writer outputs the questions.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        self.extension = ''

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

########################################################################
class JsonWriter (Writer):
    """
    The Json writer outputs the questions in Json format.
    """

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        super(JsonWriter, self).__init__()
        self.extension = '.json'

    # Public methods
    # ------------------------------------------------------------------

    def write(self, output, questions):
        super(JsonWriter, self).write()
        output.write(json.dumps(questions, default=self._serialize))

    # Protected methods
    # ------------------------------------------------------------------

    def _serialize(self, python_object):
        if isinstance(python_object, Question):
            return {
                'stem': python_object.stem,
                'options': python_object.options,
                }
        raise TypeError(repr(python_object) + ' is not really JSON serializable')
