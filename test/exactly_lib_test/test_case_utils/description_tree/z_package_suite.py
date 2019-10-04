import unittest

from exactly_lib_test.test_case_utils.description_tree import bool_trace_rendering


def suite() -> unittest.TestSuite:
    return bool_trace_rendering.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
