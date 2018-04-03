import unittest

from exactly_lib_test.test_case_utils.program.parse import parse_executable_file


def suite() -> unittest.TestSuite:
    return parse_executable_file.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
