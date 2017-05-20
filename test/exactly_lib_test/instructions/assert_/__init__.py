import unittest

from exactly_lib_test.instructions.assert_ import \
    change_dir, \
    contents, \
    run, \
    exitcode, \
    new_dir, \
    shell, \
    existence_of_file, \
    env, \
    utils
from exactly_lib_test.instructions.assert_ import stdout, stderr
from exactly_lib_test.instructions.assert_ import test_resources


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(utils.suite())
    ret_val.addTest(exitcode.suite())
    ret_val.addTest(contents.suite())
    ret_val.addTest(stdout.suite())
    ret_val.addTest(stderr.suite())
    ret_val.addTest(existence_of_file.suite())
    ret_val.addTest(new_dir.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(run.suite())
    ret_val.addTest(shell.suite())
    ret_val.addTest(env.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
