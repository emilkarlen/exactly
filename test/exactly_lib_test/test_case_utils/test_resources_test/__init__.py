import unittest

from exactly_lib_test.test_case_utils.test_resources_test import lines_transformer_assertions
from exactly_lib_test.test_case_utils.test_resources_test import sh_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sh_assertions.suite(),
        lines_transformer_assertions.suite()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
