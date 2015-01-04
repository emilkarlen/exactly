__author__ = 'emil'

import unittest

from shelltest_test.phase_instr import test_suite as phase_instr_test
from shelltest_test.exec_abs_syn import test_suite as exec_abs_syn_test
from shelltest_test.execution_files import test_write_testcase_file as script_gen_test, test_execution_directory_structure


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(phase_instr_test.suite())
    ret_val.addTest(exec_abs_syn_test.suite())
    ret_val.addTest(script_gen_test.suite())
    ret_val.addTest(test_execution_directory_structure.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
