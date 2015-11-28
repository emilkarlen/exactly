import unittest

from shellcheck_lib_test.instructions.assert_phase import test_resources
from . import change_dir
from . import contents
from . import execute
from . import exitcode
from . import new_dir
from . import shell
from . import stdout_stderr
from . import type


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(exitcode.suite())
    ret_val.addTest(contents.suite())
    ret_val.addTest(stdout_stderr.suite())
    ret_val.addTest(type.suite())
    ret_val.addTest(new_dir.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(execute.suite())
    ret_val.addTest(shell.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
