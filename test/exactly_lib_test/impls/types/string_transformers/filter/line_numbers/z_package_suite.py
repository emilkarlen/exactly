import unittest

from exactly_lib_test.impls.types.string_transformers.filter.line_numbers import ext_rsrc_dependencies, \
    invalid_range_arg
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.multi_range import \
    z_package_suite as multi_range
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.single_range import \
    z_package_suite as single_range


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_range_arg.suite(),
        ext_rsrc_dependencies.suite(),
        single_range.suite(),
        multi_range.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
