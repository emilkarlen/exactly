import unittest

from exactly_lib_test.test_case_utils.string_transformers.strip import strip_space, strip_trailing_new_lines, \
    strip_trailing_space


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        strip_trailing_new_lines.suite(),
        strip_trailing_space.suite(),
        strip_space.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
