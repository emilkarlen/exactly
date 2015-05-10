import unittest

from shelltest_test.phase_instr import test_suite as phase_instr_test
from shelltest_test.exec_abs_syn import test_suite as exec_abs_syn_test
from shelltest_test.execution import test_suite as execution_test


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(phase_instr_test.suite())
    ret_val.addTest(exec_abs_syn_test.suite())
    ret_val.addTest(execution_test.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
