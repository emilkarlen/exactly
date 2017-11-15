import unittest

from exactly_lib.help.entities.suite_reporters.objects.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib_test.help.entities.suite_reporters.test_resources.test_case_impls import \
    suite_for_suite_reporter_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
                                  suite_for_suite_reporter_documentation(suite_reporter_doc)
                                  for suite_reporter_doc in ALL_SUITE_REPORTERS
                                  ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
