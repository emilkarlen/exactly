import operator
import unittest

from exactly_lib.util import functional as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test(self):
        composition = sut.Composition(operator.neg, len)
        actual = composition(['a', 'b'])
        self.assertEqual(-2,
                         actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
