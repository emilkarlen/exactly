import unittest

from shellcheck_lib_test import act_phase_setups
from shellcheck_lib_test import cli
from shellcheck_lib_test import default
from shellcheck_lib_test import document
from shellcheck_lib_test import execution
from shellcheck_lib_test import help
from shellcheck_lib_test import instructions
from shellcheck_lib_test import test_case
from shellcheck_lib_test import test_suite
from shellcheck_lib_test import util


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(util.suite())
    ret_val.addTest(document.suite())
    ret_val.addTest(test_case.suite())
    ret_val.addTest(execution.suite())
    ret_val.addTest(cli.suite())
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(instructions.suite())
    ret_val.addTest(act_phase_setups.suite())
    ret_val.addTest(help.suite())
    ret_val.addTest(default.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
