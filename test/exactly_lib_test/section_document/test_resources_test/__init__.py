import unittest

from exactly_lib_test.section_document.test_resources_test import document_assertions
from exactly_lib_test.section_document.test_resources_test import element_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        document_assertions.suite(),
        element_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
