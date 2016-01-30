import unittest

from shellcheck_lib_test.execution.partial_execution.act_phase_tests import \
    all_phases_should_be_executed_and_result_from_action_saved_etc, \
    act_phase_should_be_transformed_to_script_file, \
    result_from_action_phase_should_be_saved, stdin_should_be_redirected_to_file_if_set_in_phase_env
from shellcheck_lib_test.execution.partial_execution.test_resources.basic import py3_test


class Test(unittest.TestCase):
    def test_act_phase_should_be_transformed_to_script_file(self):
        act_phase_should_be_transformed_to_script_file.TheTest(self).execute()

    def test_result_from_act_phase_should_be_saved(self):
        py3_test(
                self,
                result_from_action_phase_should_be_saved.TestCaseDocument().test_case,
                result_from_action_phase_should_be_saved.assertions)

    def test_stdin_should_be_redirected_to_file_if_set_in_phase_env(self):
        py3_test(
                self,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCaseDocumentThatSetsStdinFileName().test_case,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.assertions)

    def test_stdin_should_be_redirected_to_stdin_contents_if_set_in_phase_env(self):
        py3_test(
                self,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.TestCaseDocumentThatSetsStdinContents().test_case,
                stdin_should_be_redirected_to_file_if_set_in_phase_env.assertions)

    def test_all_phases_should_be_executed_and_result_from_action_saved_etc(self):
        py3_test(
                self,
                all_phases_should_be_executed_and_result_from_action_saved_etc.TestCaseDocument().test_case,
                all_phases_should_be_executed_and_result_from_action_saved_etc.assertions)


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
