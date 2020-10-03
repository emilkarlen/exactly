import unittest

from exactly_lib_test.test_case_utils.file_matcher.names.stem import configuration
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources import name_parts


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStem),
    ])


class TestStem(configuration.TestCaseBaseForStem,
               name_parts.TestNamePart):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
