import unittest

from exactly_lib_test.util.textformat.construction.section_hierarchy import z_package_suite as section_hierarchy


def suite() -> unittest.TestSuite:
    return section_hierarchy.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
