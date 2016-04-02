import unittest

from shellcheck_lib_test.instructions.configuration import home, execution_mode
from shellcheck_lib_test.instructions.configuration import test_resources


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(execution_mode.suite())
    ret_val.addTest(home.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
