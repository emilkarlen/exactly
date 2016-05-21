import unittest

from exactly_lib_test.execution.partial_execution.act_phase_tests import \
    all_phases_should_be_executed_and_result_from_action_saved_etc, \
    result_from_action_phase_should_be_saved, stdin_should_be_redirected_to_file_if_set_in_phase_env
from exactly_lib_test.execution.partial_execution.test_resources.basic import py3_test


class Test(unittest.TestCase):
    # TODO These test originate from an earlier version of the program,
    # and the test can probably be simplified using a custom
    # ActPhaseSetup (instead of using python).
    #
    # Perhaps some tests should test some slightly different features, also.
    # But is not sure about this.
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
