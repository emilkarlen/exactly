import unittest

from exactly_lib_test.common.help import see_also


def suite() -> unittest.TestSuite:
    return see_also.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
