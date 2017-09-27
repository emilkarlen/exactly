import unittest

from exactly_lib.help.syntax_elements.all_syntax_elements import ALL_SYNTAX_ELEMENT_DOCS
from exactly_lib_test.help.syntax_elements.test_resources.test_case_impls import suite_for_syntax_element_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_syntax_element_documentation(syntax_element_doc)
        for syntax_element_doc in ALL_SYNTAX_ELEMENT_DOCS
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
