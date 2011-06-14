
import json

from router import Question

########################################################################
class Writer(object):
    """
    The writer outputs the questions.
    """

    def __init__(self):
        self.extension = ''
        self.question_separator = ''

    def write(self):
        pass

########################################################################
class TextWriter (Writer):
    """
    The text writer just attempts to write the questions out in the same
    basic, tho not nessisarily identical, format.

    >>> import sys
    >>> from question import Question
    >>> q = Question()
    >>> q.stem = '1. What is the TextWriter?'
    >>> q.options.append('a. A choice-parser component.')
    >>> q.options.append('b. A Writer class.')
    >>> q.options.append('c. Both of the above.')
    >>> w = TextWriter()
    >>> w.write(sys.stdout, [q])
    1. What is the TextWriter?
    a. A choice-parser component.
    b. A Writer class.
    c. Both of the above.
    """

    def __init__(self):
        super(TextWriter, self).__init__()

    def write(self, output, questions):
        super(TextWriter, self).write()

        for question in questions:
            output.writelines((
                self.question_separator,
                #~ unicode(question.stem).encode('unicode_escape'),
                question.stem,
                '\n'))

            for option in question.options:
                output.writelines((option, '\n'))
                #~ print ('\n\nasdf:', type(option), len(option), '\nqwer:', unicode(option).encode('unicode_escape'), '\nzxcv:', option)
                #~ try:
                    #~ output.writelines((option.decode('utf-8', 'replace'), '\n'))
                #~ except TypeError:
                    #~ import pdb; pdb.set_trace()

            output.write('\n')

########################################################################
class STextWriter (TextWriter):
    """
    The separated text writer uses the TextWriter to write text with the
    questions separated by stars so that it's easier to see where each
    question starts and ends if the data is a little murky.

    >>> import sys
    >>> from question import Question
    >>> q = Question()
    >>> q.stem = '1. What is the STextWriter?'
    >>> q.options.append('a. A choice-parser component.')
    >>> q.options.append('b. A Writer class.')
    >>> q.options.append('c. Both of the above.')
    >>> STextWriter().write(sys.stdout, [q])
    ****************************************
    1. What is the STextWriter?
    a. A choice-parser component.
    b. A Writer class.
    c. Both of the above.
    """

    def __init__(self):
        super(STextWriter, self).__init__()
        self.question_separator = '\n%s\n' % ('*'*40,)

########################################################################
class JsonWriter (Writer):
    """
    The Json writer outputs the questions in Json format.

    >>> import sys
    >>> from question import Question
    >>> q = Question()
    >>> q.stem = '1. What is the JsonWriter?'
    >>> q.options.append('a. A choice-parser component.')
    >>> q.options.append('b. A Writer class.')
    >>> q.options.append('c. Both of the above.')
    >>> w = JsonWriter()
    >>> w.write(sys.stdout, [q])
    [{"options": ["a. A choice-parser component.", "b. A Writer class.", 
    "c. Both of the above."], "stem": "1. What is the JsonWriter?"}]
    """

    def __init__(self):
        super(JsonWriter, self).__init__()
        self.extension = '.json'

    def write(self, output, questions):
        super(JsonWriter, self).write()
        output.write(json.dumps(questions, default=self._serialize))

    def _serialize(self, python_object):
        if isinstance(python_object, Question):
            return {
                'stem': python_object.stem,
                'options': python_object.options,
                }
        raise TypeError(repr(python_object) + ' is not really JSON serializable')
