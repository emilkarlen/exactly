import unittest

from exactly_lib_test.common.err_msg import source_location


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        source_location.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
