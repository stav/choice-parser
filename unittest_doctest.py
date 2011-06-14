import unittest
import doctest

import choice.router as router
import choice.mogrifyer as mogrifyer
import choice.parser as parser
import choice.filter as filter
import choice.writer as writer

class TestChoiceDoctest(unittest.TestCase):

    flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

    def doctest(self, module):
        results = doctest.testmod(module, optionflags = self.flags)
        self.assertNotEqual(results.attempted, 0)
        self.assertEqual(results.failed, 0)

    def test_router(self):
        self.doctest(router)

    def test_mogrifyer(self):
        self.doctest(mogrifyer)

    def test_parser(self):
        self.doctest(parser)

    def test_filter(self):
        self.doctest(filter)

    def test_writer(self):
        self.doctest(writer)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestChoiceDoctest))
    return suite

if __name__ == '__main__':
    unittest.main()
