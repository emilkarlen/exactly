import unittest

from exactly_lib_test.test_case_utils.string_transformers.test_resources_test import \
    sdv_assertions, test_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sdv_assertions.suite(),
        test_transformers.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
