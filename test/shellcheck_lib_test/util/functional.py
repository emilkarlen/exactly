import operator
import unittest

from shellcheck_lib.util import functional as sut


class Test(unittest.TestCase):
    def test(self):
        composition = sut.Composition(operator.neg, len)
        actual = composition(['a', 'b'])
        self.assertEqual(-2,
                         actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
