import unittest

from exactly_lib_test.section_document.parse import single_file


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        single_file.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
