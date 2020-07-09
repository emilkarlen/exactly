import unittest

from exactly_lib_test.util.file_utils import tmp_file_spaces


def suite() -> unittest.TestSuite:
    return tmp_file_spaces.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
