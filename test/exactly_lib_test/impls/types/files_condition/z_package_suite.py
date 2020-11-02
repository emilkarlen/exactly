import unittest

from exactly_lib_test.impls.types.files_condition import invalid_syntax, symbol_references, file_names, \
    file_matchers, parentheses, symbol_reference


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        symbol_references.suite(),
        file_names.suite(),
        file_matchers.suite(),
        symbol_reference.suite(),
        parentheses.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
