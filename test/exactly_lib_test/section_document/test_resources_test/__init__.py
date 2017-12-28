import unittest

from exactly_lib_test.section_document.test_resources_test import section_contents_elements


def suite() -> unittest.TestSuite:
    return section_contents_elements.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
