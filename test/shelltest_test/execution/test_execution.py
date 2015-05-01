__author__ = 'emil'

import unittest

from shelltest_test.execution import test_cases


class Test(unittest.TestCase):
    def test_act_phase_should_be_transformed_to_script_file(self):
        test_cases.act_phase_should_be_transformed_to_script_file.TestCase(self).execute()

    def test_result_from_act_phase_should_be_saved(self):
        test_cases.result_from_action_phase_should_be_saved.TestCase(self).execute()

    def test_environment_variables_should_be_accessible_in_all_phases(self):
        test_cases.execution_environment_variables.TestCase(self).execute()

    def test_cwd_at_start_of_each_phase_should_be_test_root_dir(self):
        test_cases.cwd_at_start_of_each_phase_should_be_test_root_dir.TestCase(self).execute()

    def test_all_phases_should_be_executed_and_result_from_action_saved_etc(self):
        test_cases.all_phases_should_be_executed_and_result_from_action_saved_etc.TestCase(self).execute()

    def test_stdin_should_be_redirected_to_file_if_set_in_phase_env(self):
        test_cases.stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCase(self).execute()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
