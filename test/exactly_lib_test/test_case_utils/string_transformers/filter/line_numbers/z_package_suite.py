import unittest

from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers import upper_limit, \
    ext_rsrc_dependencies, lower_limit, lower_upper_limit, invalid_range_arg, single_int


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_range_arg.suite(),
        ext_rsrc_dependencies.suite(),
        single_int.suite(),
        upper_limit.suite(),
        lower_limit.suite(),
        lower_upper_limit.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
