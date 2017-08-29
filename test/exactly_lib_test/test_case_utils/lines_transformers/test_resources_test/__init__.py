import unittest

from exactly_lib_test.test_case_utils.lines_transformers.test_resources_test import lines_transformer_assertions


def suite() -> unittest.TestSuite:
    return lines_transformer_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
