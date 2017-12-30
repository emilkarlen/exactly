import unittest

from exactly_lib_test.section_document.test_resources_test import section_element_parser_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        section_element_parser_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
