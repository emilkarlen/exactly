import unittest

from exactly_lib_test.util.simple_textstruct.file_printer_output import line_element, minor_block, \
    major_block_and_document


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        line_element.suite(),
        minor_block.suite(),
        major_block_and_document.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
