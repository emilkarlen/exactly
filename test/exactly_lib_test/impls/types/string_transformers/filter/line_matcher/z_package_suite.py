import unittest

from exactly_lib_test.impls.types.string_transformers.filter.line_matcher import basics, lines_interval_opt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        basics.suite(),
        lines_interval_opt.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
