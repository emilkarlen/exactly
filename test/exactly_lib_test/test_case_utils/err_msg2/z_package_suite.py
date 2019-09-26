import unittest

from exactly_lib_test.test_case_utils.err_msg2 import trace_rendering


def suite() -> unittest.TestSuite:
    return trace_rendering.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
