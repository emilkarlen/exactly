import unittest

from exactly_lib_test.instructions.setup import \
    change_dir, run, copy, new_file, new_dir, shell, stdin, utils, env, define_symbol
from exactly_lib_test.instructions.setup import test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(utils.suite())
    ret_val.addTest(copy.suite())
    ret_val.addTest(shell.suite())
    ret_val.addTest(run.suite())
    ret_val.addTest(env.suite())
    ret_val.addTest(stdin.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(new_file.suite())
    ret_val.addTest(new_dir.suite())
    ret_val.addTest(define_symbol.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
