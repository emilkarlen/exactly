import unittest

from exactly_lib_test.instructions.assert_.contents_of_dir import non_recursive, recursive, recursive_w_depth_limits


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        non_recursive.suite(),
        recursive.suite(),
        recursive_w_depth_limits.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
