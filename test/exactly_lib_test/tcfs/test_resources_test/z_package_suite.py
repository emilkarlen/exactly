import unittest

from exactly_lib_test.tcfs.test_resources_test import \
    path_relativity, hds_populators, hds_utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        path_relativity.suite(),
        hds_populators.suite(),
        hds_utils.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
