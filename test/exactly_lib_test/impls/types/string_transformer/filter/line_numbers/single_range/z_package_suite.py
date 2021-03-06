import unittest

from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.single_range import lower_limit, \
    lower_upper_limit, single_int, upper_limit


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        single_int.suite(),
        upper_limit.suite(),
        lower_limit.suite(),
        lower_upper_limit.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
