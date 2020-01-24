import unittest

from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir import non_recursive


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        non_recursive.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
