import unittest

from .formatting_test_impls import paragraph


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(paragraph.suite())
    return ret_val


if __name__ == '__main__':
    unittest.main()
