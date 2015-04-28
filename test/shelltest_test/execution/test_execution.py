__author__ = 'emil'

import unittest

from shelltest_test.execution.test_cases import execution_environment_variables

from shelltest_test.execution.test_cases import result_from_action_phase_should_be_saved
from shelltest_test.execution.test_cases import cwd_at_start_of_each_phase_should_be_test_root_dir
from shelltest_test.execution.test_cases import all_phases_should_be_executed_and_result_from_action_saved_etc
from shelltest_test.execution.test_cases import stdin_should_be_redirected_to_file_if_set_in_phase_env
from shelltest_test.execution.test_cases import act_phase_should_be_transformed_to_script_file


class Test(unittest.TestCase):
    def test_act_phase_should_be_transformed_to_script_file(self):
        act_phase_should_be_transformed_to_script_file.TestCase(self).execute()

    def test_result_from_act_phase_should_be_saved(self):
        result_from_action_phase_should_be_saved.TestCase2(self).execute()

    def test_environment_variables_should_be_accessible_in_all_phases(self):
        execution_environment_variables.TestCase(self).execute()

    def test_cwd_at_start_of_each_phase_should_be_test_root_dir2(self):
        cwd_at_start_of_each_phase_should_be_test_root_dir.TestCase2(self).execute()

    def test_all_phases_should_be_executed_and_result_from_action_saved_etc(self):
        all_phases_should_be_executed_and_result_from_action_saved_etc.TestCase(self).execute()

    def test_stdin_should_be_redirected_to_file_if_set_in_phase_env2(self):
        stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCase(self).execute()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
