import unittest

from exactly_lib_test.common.report_rendering import source_location
from exactly_lib_test.common.report_rendering.description_tree import z_package_suite as description_tree


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        source_location.suite(),
        description_tree.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
