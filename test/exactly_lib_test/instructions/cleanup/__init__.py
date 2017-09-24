import unittest

from exactly_lib_test.instructions.cleanup import change_dir, env, run, new_dir, shell, transform
from exactly_lib_test.instructions.cleanup import test_resources, utils


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(utils.suite())
    ret_val.addTest(shell.suite())
    ret_val.addTest(run.suite())
    ret_val.addTest(env.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(new_dir.suite())
    ret_val.addTest(transform.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
