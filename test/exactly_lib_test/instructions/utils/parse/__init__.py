import unittest

from exactly_lib_test.instructions.utils.parse import parse_executable_file


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse_executable_file.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
