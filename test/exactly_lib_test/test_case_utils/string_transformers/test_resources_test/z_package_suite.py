import unittest

from exactly_lib_test.test_case_utils.string_transformers.test_resources_test import \
    test_transformers


def suite() -> unittest.TestSuite:
    return test_transformers.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
