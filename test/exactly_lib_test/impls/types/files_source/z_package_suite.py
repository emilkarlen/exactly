import unittest

from exactly_lib_test.impls.types.files_source.parse import z_package_suite as parse


def suite() -> unittest.TestSuite:
    return parse.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
