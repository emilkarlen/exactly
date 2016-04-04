import unittest

from shellcheck_lib_test.util.textformat.formatting.html import paragraph


def suite() -> unittest.TestSuite:
    return paragraph.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
