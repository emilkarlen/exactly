import unittest

from exactly_lib_test.test_suite.reporters import simple_progress_reporter


def suite() -> unittest.TestSuite:
    return simple_progress_reporter.suite()


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
