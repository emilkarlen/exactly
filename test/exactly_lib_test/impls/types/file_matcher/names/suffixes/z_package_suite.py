import unittest

from exactly_lib_test.impls.types.file_matcher.names.suffixes import common, specific


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        specific.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
