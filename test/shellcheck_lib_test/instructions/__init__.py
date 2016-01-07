import unittest

from shellcheck_lib_test.instructions import assert_phase
from shellcheck_lib_test.instructions import before_assert
from shellcheck_lib_test.instructions import cleanup
from shellcheck_lib_test.instructions import configuration
from shellcheck_lib_test.instructions import multi_phase_instructions
from shellcheck_lib_test.instructions import setup
from shellcheck_lib_test.instructions import utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(utils.suite())
    ret_val.addTest(multi_phase_instructions.suite())
    ret_val.addTest(configuration.suite())
    ret_val.addTest(setup.suite())
    ret_val.addTest(before_assert.suite())
    ret_val.addTest(assert_phase.suite())
    ret_val.addTest(cleanup.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
