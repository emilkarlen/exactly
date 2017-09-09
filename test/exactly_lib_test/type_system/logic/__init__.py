import unittest

from exactly_lib_test.type_system.logic import file_matcher


def suite() -> unittest.TestSuite:
    return file_matcher.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
