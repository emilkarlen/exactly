import unittest

from exactly_lib_test.instructions.assert_.contents_of_dir import common, empty, num_files, quant_over_files, \
    multi_line_syntax, symbol_reference


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        empty.suite(),
        num_files.suite(),
        quant_over_files.suite(),
        symbol_reference.suite(),
        multi_line_syntax.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
