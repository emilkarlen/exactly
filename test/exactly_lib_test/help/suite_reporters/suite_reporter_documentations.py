import unittest

from exactly_lib.help.suite_reporters.suite_reporter.all_suite_reporters import ALL_SUITE_REPORTER
from exactly_lib_test.help.suite_reporters.test_resources.test_case_impls import suite_for_suite_reporter_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
                                  suite_for_suite_reporter_documentation(suite_reporter_doc)
                                  for suite_reporter_doc in ALL_SUITE_REPORTER
                                  ])


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
