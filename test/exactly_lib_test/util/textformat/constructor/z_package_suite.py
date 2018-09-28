import unittest

from exactly_lib_test.util.textformat.constructor import paragraphs


def suite() -> unittest.TestSuite:
    return paragraphs.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
