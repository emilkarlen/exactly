import unittest

from exactly_lib_test.common.err_msg import utils, source_location


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        utils.suite(),
        source_location.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
