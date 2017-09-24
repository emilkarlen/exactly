import unittest

from exactly_lib_test.instructions.setup import \
    change_dir, run, install, new_file, new_dir, shell, stdin, utils, env, assign_symbol, transform
from exactly_lib_test.instructions.setup import test_resources


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(utils.suite())
    ret_val.addTest(install.suite())
    ret_val.addTest(shell.suite())
    ret_val.addTest(run.suite())
    ret_val.addTest(env.suite())
    ret_val.addTest(stdin.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(new_file.suite())
    ret_val.addTest(new_dir.suite())
    ret_val.addTest(assign_symbol.suite())
    ret_val.addTest(transform.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
