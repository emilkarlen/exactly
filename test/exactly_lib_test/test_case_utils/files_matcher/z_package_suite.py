import unittest

from exactly_lib_test.test_case_utils.files_matcher import common, empty, num_files, quant_over_files, \
    symbol_reference, selections


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        empty.suite(),
        num_files.suite(),
        quant_over_files.suite(),
        symbol_reference.suite(),
        selections.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
