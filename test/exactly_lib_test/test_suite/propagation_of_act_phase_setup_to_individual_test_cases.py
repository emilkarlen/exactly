import pathlib
import unittest

from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.test_case import test_case_processing
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_set import INSTRUCTION_NAME__ACTOR
from exactly_lib.test_suite.reporting import SubSuiteReporter
from exactly_lib.test_suite.suite_hierarchy_reading import Environment
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.python_program_execution import abs_path_to_interpreter_quoted_for_exactly, \
    abs_path_to_interpreter
from exactly_lib_test.test_suite.test_resources.check_full_execution import Setup, check
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingRootSuiteReporter, \
    ExecutionTracingSubSuiteProgressReporter, CaseEndInfo


class TestActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite(unittest.TestCase):
    def runTest(self):
        check(ActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite(), self)


class TestActorIsNotPropagatedToSubSuites(unittest.TestCase):
    def runTest(self):
        check(ActorIsNotPropagatedToSubSuites(), self)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestActorIsPropagatedToEveryTestCaseThatIsListedDirectlyInTheSuite))
    ret_val.addTest(unittest.makeSuite(TestActorIsNotPropagatedToSubSuites))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class SetupForSuccessfulExecution(Setup):
    def test_case_handling_setup(self) -> Environment:
        return Environment(IDENTITY_PREPROCESSOR,
                           single_command_setup.act_phase_setup())

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
                     py_executable,
                     # TODO want a quoted path here, so that it works on Windows.
                     # But ExecutableFileInstruction doesn't handle quoted paths for the moment.
                 ])),
        ])


def _set_actor_for_running(quoted_name_of_executable) -> str:
    return INSTRUCTION_NAME__ACTOR + ' ' + quoted_name_of_executable


def _assert_every_test_case_to_pass(put: unittest.TestCase,
                                    reporter: ExecutionTracingRootSuiteReporter):
    def assert_is_pass(case_end_info: CaseEndInfo):
        result = case_end_info.result
        if result.status is not test_case_processing.Status.EXECUTED:
            msg = 'Expected: %s. Actual: %s.\nFor %s' % (test_case_processing.Status.EXECUTED,
                                                         result.status,
                                                         str(case_end_info.case.file_path))

            put.fail(msg)
        if result.execution_result.status is not FullResultStatus.PASS:
            msg = 'Expected: %s. Actual: %s.\nFor %s.\n%s' % (FullResultStatus.PASS,
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
