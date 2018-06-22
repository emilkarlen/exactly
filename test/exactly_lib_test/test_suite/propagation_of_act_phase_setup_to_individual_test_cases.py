import pathlib
import unittest

from exactly_lib.act_phase_setups import command_line
from exactly_lib.definitions.test_suite.instruction_names import INSTRUCTION_NAME__ACTOR
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.instructions.configuration.utils.actor_utils import SOURCE_INTERPRETER_OPTION
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite.reporting import SubSuiteReporter
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.programs.python_program_execution import \
    abs_path_to_interpreter_quoted_for_exactly, \
    abs_path_to_interpreter
from exactly_lib_test.test_suite.test_resources.check_full_execution import Setup, check
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingRootSuiteReporter, \
    ExecutionTracingSubSuiteProgressReporter, CaseEndInfo


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite))
    ret_val.addTest(unittest.makeSuite(TestActorIsNotPropagatedToSubSuites))
    return ret_val


class TestActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite(unittest.TestCase):
    def runTest(self):
        check(ActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite(), self)


class TestActorIsNotPropagatedToSubSuites(unittest.TestCase):
    def runTest(self):
        check(ActorIsNotPropagatedToSubSuites(), self)


class SetupForSuccessfulExecution(Setup):
    def test_case_handling_setup(self) -> TestCaseHandlingSetup:
        return TestCaseHandlingSetup(command_line.act_phase_setup(),
                                     IDENTITY_PREPROCESSOR)

    def assertions(self,
                   put: unittest.TestCase,
                   reporter: ExecutionTracingRootSuiteReporter,
                   actual_exit_code: int):
        put.assertEqual(ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                        actual_exit_code,
                        'Expecting the suite be be valid (and thus to have been executed).')
        _assert_every_test_case_to_pass(put, reporter)


class ActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite(SetupForSuccessfulExecution):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        py_executable = abs_path_to_interpreter_quoted_for_exactly()
        test_case_with_py_actor = lines_content(['[act]',
                                                 'import sys',
                                                 'sys.exit(0)',
                                                 ])
        return DirContents([
            File('main.suite',
                 lines_content(['[conf]',
                                _set_actor_for_running(py_executable),
                                '[cases]',
                                '1-in-main-suite.case',
                                '2-in-main-suite.case',
                                ])),
            File('1-in-main-suite.case',
                 test_case_with_py_actor),
            File('2-in-main-suite.case',
                 test_case_with_py_actor),
        ])


class ActorIsNotPropagatedToSubSuites(SetupForSuccessfulExecution):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        py_executable = abs_path_to_interpreter()
        return DirContents([
            File('main.suite',
                 lines_content(['[conf]',
                                _set_actor_for_running(py_executable),
                                '[suites]',
                                'sub.suite',
                                ])),
            File('sub.suite',
                 lines_content(['[cases]',
                                'in-sub-suite-that-is-expected-to-have-default-actor.case'])),
            File('in-sub-suite-that-is-expected-to-have-default-actor.case',
                 lines_content([
                     '[act]',
                     abs_path_to_interpreter_quoted_for_exactly(),
                 ])),
        ])


def _set_actor_for_running(quoted_name_of_executable) -> str:
    return '{actor_instruction} = {actor_option} {actor_executable}'.format(
        actor_instruction=INSTRUCTION_NAME__ACTOR,
        actor_option=SOURCE_INTERPRETER_OPTION,
        actor_executable=quoted_name_of_executable)


def _assert_every_test_case_to_pass(put: unittest.TestCase,
                                    reporter: ExecutionTracingRootSuiteReporter):
    def assert_is_pass(case_end_info: CaseEndInfo):
        result = case_end_info.result
        if result.status is not test_case_processing.Status.EXECUTED:
            msg = 'Expected: %s. Actual: %s.\nFor %s' % (test_case_processing.Status.EXECUTED,
                                                         result.status,
                                                         str(case_end_info.case.file_path))

            put.fail(msg)
        if result.execution_result.status is not FullExeResultStatus.PASS:
            msg = 'Expected: %s. Actual: %s.\nFor %s.\n%s' % (FullExeResultStatus.PASS,
                                                              result.execution_result.status,
                                                              str(case_end_info.case.file_path),
                                                              str(result.execution_result.failure_info.failure_details))
            put.fail(msg)

    for sub_suite_reporter in reporter.sub_suite_reporters:
        assert isinstance(sub_suite_reporter, SubSuiteReporter)
        listener = sub_suite_reporter.listener()
        assert isinstance(listener, ExecutionTracingSubSuiteProgressReporter)
        for case_end_info in listener.case_end_list:
            assert isinstance(case_end_info, CaseEndInfo)
            assert_is_pass(case_end_info)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
