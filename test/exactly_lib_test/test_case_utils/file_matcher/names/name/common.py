import unittest

from exactly_lib_test.test_case_utils.file_matcher.names.name import configuration
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources import syntax_and_validation, glob_pattern, \
    reg_ex


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSyntax),
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestGlobPattern),
        unittest.makeSuite(TestRegEx),
    ])


class TestSyntax(configuration.TestCaseBaseForName,
                 syntax_and_validation.TestSyntax):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestValidation(configuration.TestCaseBaseForName,
                     syntax_and_validation.TestValidation):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSymbolReferences(configuration.TestCaseBaseForName,
                           syntax_and_validation.TestSymbolReferences):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestGlobPattern(configuration.TestCaseBaseForName,
                      glob_pattern.TestGlobPattern):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestRegEx(configuration.TestCaseBaseForName,
                reg_ex.TestRegEx):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass
