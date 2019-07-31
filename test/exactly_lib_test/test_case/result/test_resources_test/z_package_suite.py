import unittest

from exactly_lib_test.test_case.result.test_resources_test import sh_assertions, pfh_assertions, svh_assertions, \
    failure_details_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sh_assertions.suite(),
        pfh_assertions.suite(),
        svh_assertions.suite(),
        failure_details_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
