import unittest

from exactly_lib_test.test_case_utils.string_models import model_from_lines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        model_from_lines.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
