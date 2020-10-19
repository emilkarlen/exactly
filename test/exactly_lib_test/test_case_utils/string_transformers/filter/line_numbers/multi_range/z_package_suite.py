import unittest

from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers.multi_range import test_resources_test, \
    range_merge, non_neg_limits, some_neg_limits, invalid_range_arg


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        range_merge.suite(),
        invalid_range_arg.suite(),
        non_neg_limits.suite(),
        some_neg_limits.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
