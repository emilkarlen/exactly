import unittest

from exactly_lib_test.test_case_utils.files_matcher import common, empty, num_files, quant_over_files, \
    selections, std_expr


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        std_expr.suite(),
        empty.suite(),
        num_files.suite(),
        quant_over_files.suite(),
        selections.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
