import unittest

from shellcheck_lib_test.instructions.setup import test_resources
from . import change_dir
from . import env
from . import execute
from . import install
from . import new_file
from . import shell
from . import stdin
from . import utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(utils.suite())
    ret_val.addTest(install.suite())
    ret_val.addTest(shell.suite())
    ret_val.addTest(execute.suite())
    ret_val.addTest(env.suite())
    ret_val.addTest(stdin.suite())
    ret_val.addTest(change_dir.suite())
    ret_val.addTest(new_file.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
