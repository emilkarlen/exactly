import unittest

from exactly_lib_test.processing.test_resources_test import result_assertions, test_case_processing_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        result_assertions.suite(),
        test_case_processing_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
