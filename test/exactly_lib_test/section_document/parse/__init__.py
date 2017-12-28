import unittest

from exactly_lib_test.section_document.parse import single_file, test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        single_file.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
