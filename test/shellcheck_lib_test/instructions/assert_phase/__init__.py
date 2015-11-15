import unittest

from shellcheck_lib_test.instructions.assert_phase import test_resources
from . import exitcode
from . import contents
from . import stdout_stderr
from . import type
from . import mkdir
from . import change_dir


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(exitcode.suite())
    ret_val.addTest(contents.suite())
    ret_val.addTest(stdout_stderr.suite())
    ret_val.addTest(type.suite())
    ret_val.addTest(mkdir.suite())
    ret_val.addTest(change_dir.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
