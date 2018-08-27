import unittest

from exactly_lib_test.section_document.document_parser import \
    section_configuration, \
    section_handling, \
    single_file, \
    file_inclusions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        section_configuration.suite(),
        section_handling.suite(),
        single_file.suite(),
        file_inclusions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
