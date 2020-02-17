import unittest

from exactly_lib_test.test_case_utils.files_condition import invalid_syntax, symbol_references, file_names, \
    file_matchers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        symbol_references.suite(),
        file_names.suite(),
        file_matchers.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
