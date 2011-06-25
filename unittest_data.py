import unittest

from choice.router import Router

class TestChoiceData(unittest.TestCase):

    def setUp(self):
        self.router = Router()

    def tearDown(self):
        self.router = None

    def test_anarchy(self):
        self.router.load(['-i', 'input/anarchy'])
        self.assertEqual(len(self.router.questions), 10)

    def test_drivers(self):
        self.router.load(['-i', 'input/drivers'])
        self.assertEqual(len(self.router.questions), 11)

    def test_reading(self):
        self.router.load(['-i', 'input/reading'])
        self.assertEqual(len(self.router.questions), 15)

    def test_writing(self):
        self.router.load(['-i', 'input/writing'])
        self.assertEqual(len(self.router.questions), 10)

    def test_choices(self):
        self.router.load('-i input/choices  -m BooleanoptionMogrifyer,SplitstemMogrifyer'.split())
        self.assertEqual(len(self.router.questions), 7)

    def test_teachers(self):
        self.router.load(['-i', 'input/teachers.pdf'])
        self.assertEqual(len(self.router.questions), 14)

    def test_victoria(self):
        self.router.load(['-i', 'input/victoria'])
        self.assertEqual(len(self.router.questions), 10)

    def test_computer(self):
        self.router.load(['-i', 'input/computer.pdf'])
        self.assertEqual(len(self.router.questions), 20)

    # def test_imhotep(self):
    #     self.router.load('-i input/imhotep  -m SplitstemMogrifyer'.split())
    #     self.assertEqual(len(self.router.questions), 11)

    def test_motorcycle(self):
        self.router.load(['-i', 'input/motorcycle'])
        self.assertEqual(len(self.router.questions), 10)

    def test_vocabulary(self):
        self.router.load(['-i', 'input/vocabulary.pdf'])
        self.assertEqual(len(self.router.questions), 6)

    def test_pharmacology(self):
        self.router.load('-i input/pharmacology.pdf'.split())
        self.assertTrue(len(self.router.questions) > 250)

    def test_regulation(self):
        self.router.load(['-i', 'input/regulation.pdf'])
        self.assertEqual(len(self.router.questions), 20)

    # def test_accounting(self):
    #     self.router.load(['-i', 'input/accounting.txt'])
    #     self.assertTrue(len(self.router.questions) > 300)
        
    def test_plants(self):
        self.router.load(['-i', 'input/plants.pdf'])
        # 56 questions minus 5 short answer
        self.assertEqual(len(self.router.questions), 51)
        
    def test_money(self):
        self.router.load(['-i', 'input/money.pdf'])
        self.assertEqual(len(self.router.questions), 23)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestChoiceData))
    return suite

if __name__ == '__main__':
    unittest.main()
