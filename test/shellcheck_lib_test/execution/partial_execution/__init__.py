import unittest

from shellcheck_lib_test.execution.partial_execution.test_cases import \
    all_phases_should_be_executed_and_result_from_action_saved_etc, \
    act_phase_should_be_transformed_to_script_file, \
    result_from_action_phase_should_be_saved, stdin_should_be_redirected_to_file_if_set_in_phase_env
from shellcheck_lib_test.execution.test_resources import py_unit_test_case


class Test(unittest.TestCase):
    def test_act_phase_should_be_transformed_to_script_file(self):
        py_unit_test_case.py3_test(
                self,
                act_phase_should_be_transformed_to_script_file.TestCaseDocument().test_case,
                act_phase_should_be_transformed_to_script_file.assertions)

    def test_result_from_act_phase_should_be_saved(self):
        py_unit_test_case.py3_test(
                self,
                result_from_action_phase_should_be_saved.TestCaseDocument().test_case,
                result_from_action_phase_should_be_saved.assertions)

    def test_stdin_should_be_redirected_to_file_if_set_in_phase_env(self):
        py_unit_test_case.py3_test(
                self,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCaseDocumentThatSetsStdinFileName().test_case,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.assertions)

    def test_stdin_should_be_redirected_to_stdin_contents_if_set_in_phase_env(self):
        py_unit_test_case.py3_test(
                self,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCaseDocumentThatSetsStdinContents().test_case,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.assertions)

    def test_all_phases_should_be_executed_and_result_from_action_saved_etc(self):
        py_unit_test_case.py3_test(
                self,
                all_phases_should_be_executed_and_result_from_action_saved_etc.TestCaseDocument().test_case,
                all_phases_should_be_executed_and_result_from_action_saved_etc.assertions)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    unittest.main()
