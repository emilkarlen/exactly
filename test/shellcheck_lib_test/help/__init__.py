import unittest

from shellcheck_lib_test.help import program_modes, concepts


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(program_modes.suite())
    ret_val.addTest(concepts.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
