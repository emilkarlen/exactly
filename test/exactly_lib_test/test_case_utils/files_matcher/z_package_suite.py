import unittest

from exactly_lib_test.test_case_utils.files_matcher import common, empty, num_files, quant_over_files, symbol_reference
from exactly_lib_test.test_case_utils.files_matcher.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        common.suite(),
        empty.suite(),
        num_files.suite(),
        quant_over_files.suite(),
        symbol_reference.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
