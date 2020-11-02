import unittest

from exactly_lib_test.impls.types.files_matcher.models import non_recursive, recursive


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        non_recursive.suite(),
        recursive.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
