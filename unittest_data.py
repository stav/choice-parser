import unittest

from router import Router
from parser import IndexParser
from parser import BlockParser
from parser import ChunkParser

class TestChoiceData(unittest.TestCase):

    def setUp(self):
        self.router = Router()

    def tearDown(self):
        self.router = None

    def test_anarchy(self):
        self.router.load(['-i', 'input/anarchy', '-s'])
        self.assertTrue(self.router.parser, IndexParser)
        self.assertEqual(len(self.router.questions), 10)

    def test_drivers(self):
        self.router.load(['-i', 'input/drivers', '-s'])
        self.assertTrue(self.router.parser, BlockParser)
        self.assertEqual(len(self.router.questions), 11)

    def test_reading(self):
        self.router.load(['-i', 'input/reading', '-s'])
        self.assertTrue(self.router.parser, IndexParser)
        self.assertEqual(len(self.router.questions), 15)

    def test_choices(self):
        self.router.load(['-i', 'input/writing', '-s'])
        self.assertTrue(self.router.parser, IndexParser)
        self.assertEqual(len(self.router.questions), 10)

    def test_coices(self):
        self.router.load(['-i', 'input/choices', '-m', 'BooleanoptionMogrifyer', '-s'])
        self.assertTrue(self.router.parser, IndexParser)
        self.assertEqual(len(self.router.questions), 7)

    def test_teachers(self):
        self.router.load(['-i', 'input/teachers.pdf', '-s'])
        self.assertTrue(self.router.parser, IndexParser)
        self.assertEqual(len(self.router.questions), 14)

    def test_victoria(self):
        self.router.load(['-i', 'input/victoria', '-s'])
        self.assertTrue(self.router.parser, ChunkParser)
        self.assertEqual(len(self.router.questions), 10)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestChoiceData))
    return suite

if __name__ == '__main__':
    unittest.main()
