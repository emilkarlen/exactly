import unittest

from exactly_lib_test.section_document.parse import single_file, file_inclusions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        single_file.suite(),
        file_inclusions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
