__author__ = 'emil'

import os

import unittest

from shelltest_test.execution.test_cases import execution_environment_variables
from shelltest_test.execution.test_cases import result_from_action_phase_should_be_saved
from shelltest_test.execution.test_cases import cwd_at_start_of_each_phase_should_be_test_root_dir
from shelltest_test.execution.test_cases import all_phases_should_be_executed_and_result_from_action_saved_etc
from shelltest_test.execution.test_cases import stdin_should_be_redirected_to_file_if_set_in_phase_env


class Test(unittest.TestCase):
    def test_result_from_act_phase_should_be_saved(self):
        Test.run_with_preserved_cwd(result_from_action_phase_should_be_saved.TestCase(self))

    def test_environment_variables_should_be_accessible_in_all_phases(self):
        Test.run_with_preserved_cwd(execution_environment_variables.TestCase(self))

    def test_cwd_at_start_of_each_phase_should_be_test_root_dir(self):
        Test.run_with_preserved_cwd(cwd_at_start_of_each_phase_should_be_test_root_dir.TestCase(self))

    def test_all_phases_should_be_executed_and_result_from_action_saved_etc(self):
        Test.run_with_preserved_cwd(all_phases_should_be_executed_and_result_from_action_saved_etc.TestCase(self))

    def test_stdin_should_be_redirected_to_file_if_set_in_phase_env(self):
        Test.run_with_preserved_cwd(stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCase(self))

    @staticmethod
    def run_with_preserved_cwd(tc):
        cwd_before_test = os.getcwd()
        tc.execute()
        os.chdir(cwd_before_test)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
