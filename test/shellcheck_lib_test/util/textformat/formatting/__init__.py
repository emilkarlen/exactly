import unittest

from shellcheck_lib_test.util.textformat.formatting import text


def suite() -> unittest.TestSuite:
    return text.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
