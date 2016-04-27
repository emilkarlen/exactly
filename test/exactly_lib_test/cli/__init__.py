import unittest

from exactly_lib_test.cli import program_modes


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(program_modes.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
