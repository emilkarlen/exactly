import os
import unittest

from exactly_lib.instructions.multi_phase_instructions import run as sut
from exactly_lib.instructions.utils import sub_process_execution as spe
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_TMP_OPTION
from exactly_lib.instructions.utils.instruction_from_parts_for_executing_sub_process import SubProcessExecutionSetup, \
    MainStepExecutorForSubProcess
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case import os_services
from exactly_lib.test_case.phases.common import HomeAndSds, PhaseLoggingPaths, InstructionEnvironmentForPostSdsStep
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources import home_and_sds_test
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution.utils import HomeAndSdsAction
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.parse import single_line_source
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class ExecuteAction(HomeAndSdsAction):
    def __init__(self,
                 source_info: spe.InstructionSourceInfo,
                 setup: SubProcessExecutionSetup):
        self.setup = setup
        self.source_info = source_info

    def apply(self,
              home_and_sds: HomeAndSds) -> spe.ResultAndStderr:
        executor = MainStepExecutorForSubProcess(self.source_info, self.setup)
        return executor.apply(InstructionEnvironmentForPostSdsStep(home_and_sds.home_dir_path,
                                                                   dict(os.environ),
                                                                   home_and_sds.sds,
                                                                   'the-phase'),
                              PhaseLoggingPaths(home_and_sds.sds.log_dir, 'the-phase'),
                              os_services.new_default())


class TestCaseBase(home_and_sds_test.TestCaseBase):
    def _check_source(self,
                      source: SingleInstructionParserSource,
                      arrangement: home_and_sds_test.Arrangement,
                      expectation: home_and_sds_test.Expectation):
        source_info = spe.InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                'instruction-name')
        setup = sut.SetupParser().apply(source)
        action = ExecuteAction(source_info, setup)
        self._check(action, arrangement, expectation)


class IsSuccess(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: spe.ResultAndStderr,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertTrue(value.result.is_success,
                       message_builder.apply('Result is expected to indicate success'))


class IsFailure(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value: spe.ResultAndStderr,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertFalse(value.result.is_success,
                        message_builder.apply('Result is expected to indicate failure'))


class ExitCodeIs(va.ValueAssertion):
    def __init__(self,
                 exit_code: int):
        self.exit_code = exit_code

    def apply(self,
              put: unittest.TestCase,
              value: spe.ResultAndStderr,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertEquals(self.exit_code,
                         value.result.exit_code,
                         message_builder.apply('Exit code'))


class StderrContentsIs(va.ValueAssertion):
    def __init__(self,
                 stderr_contents: str):
        self.stderr_contents = stderr_contents

    def apply(self,
              put: unittest.TestCase,
              value: spe.ResultAndStderr,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertEqual(self.stderr_contents,
                        value.stderr_contents,
                        message_builder.apply('Stderr contents'))


def is_success_result(exitcode: int,
                      stderr_contents: str) -> va.ValueAssertion:
    return va.And([IsSuccess(),
                   ExitCodeIs(exitcode),
                   StderrContentsIs(stderr_contents)])


class TestExecuteProgramWithShellArgumentList(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._check_source(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                           home_and_sds_test.Arrangement(),
                           home_and_sds_test.Expectation(expected_action_result=is_success_result(0,
                                                                                                  None)))

    def test_double_dash_should_invoke_execute(self):
        argument = py_exe.command_line_for_executing_program_via_command_line(
            'exit(0)',
            args_directly_after_interpreter='--')
        self._check_source(single_line_source(argument),
                           home_and_sds_test.Arrangement(),
                           home_and_sds_test.Expectation(expected_action_result=is_success_result(0,
                                                                                                  None)))

    def test_check_non_zero_exit_code(self):
        self._check_source(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                           home_and_sds_test.Arrangement(),
                           home_and_sds_test.Expectation(expected_action_result=is_success_result(1,
                                                                                                  '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write(\\"on stderr\\"); exit(2)'
        self._check_source(
            single_line_source(py_exe.command_line_for_executing_program_via_command_line(python_program)),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=is_success_result(2,
                                                                                   'on stderr')))

    def test_invalid_executable(self):
        self._check_source(single_line_source('/not/an/executable/program'),
                           home_and_sds_test.Arrangement(),
                           home_and_sds_test.Expectation(expected_action_result=IsFailure()))


class TestExecuteInterpret(TestCaseBase):
    def test_check_zero_exit_code__rel_home_default(self):
        self._check_source(single_line_source(py_exe.command_line_for_arguments([sut.INTERPRET_OPTION,
                                                                                 'exit-with-value-on-command-line.py',
                                                                                 0])),
                           home_and_sds_test.Arrangement(
                               home_dir_contents_before=DirContents([
                                   File('exit-with-value-on-command-line.py',
                                        py_pgm_that_exits_with_value_on_command_line(''))])),
                           home_and_sds_test.Expectation(
                               expected_action_result=is_success_result(0,
                                                                        None),

                           )
                           )

    def test_check_zero_exit_code__rel_tmp(self):
        self._check_source(single_line_source(py_exe.command_line_for_arguments([sut.INTERPRET_OPTION,
                                                                                 REL_TMP_OPTION,
                                                                                 'exit-with-value-on-command-line.py',
                                                                                 0])),
                           home_and_sds_test.Arrangement(
                               sds_contents_before=sds_populator.tmp_user_dir_contents(DirContents([
                                   File('exit-with-value-on-command-line.py',
                                        py_pgm_that_exits_with_value_on_command_line(''))]))),
                           home_and_sds_test.Expectation(
                               expected_action_result=is_success_result(0,
                                                                        None)),
                           )

    def test_check_non_zero_exit_code(self):
        self._check_source(single_line_source(py_exe.command_line_for_arguments([sut.INTERPRET_OPTION,
                                                                                 'exit-with-value-on-command-line.py',
                                                                                 2])),
                           home_and_sds_test.Arrangement(
                               home_dir_contents_before=DirContents([
                                   File('exit-with-value-on-command-line.py',
                                        py_pgm_that_exits_with_value_on_command_line('on stderr'))])),
                           home_and_sds_test.Expectation(
                               expected_action_result=is_success_result(2,
                                                                        'on stderr'),

                           )
                           )

    def test_invalid_executable(self):
        argument = '/not/an/executable/program {} {} {}'.format(sut.INTERPRET_OPTION,
                                                                'exit-with-value-on-command-line.py',
                                                                0)
        self._check_source(single_line_source(argument),
                           home_and_sds_test.Arrangement(
                               home_dir_contents_before=DirContents([
                                   File('exit-with-value-on-command-line.py',
                                        py_pgm_that_exits_with_value_on_command_line(''))])),
                           home_and_sds_test.Expectation(
                               expected_action_result=IsFailure(),

                           ))


class TestSource(TestCaseBase):
    def test_parse_should_fail_when_no_source_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.SetupParser().apply(single_line_source('EXECUTABLE %s' % sut.SOURCE_OPTION))

    def test_check_zero_exit_code(self):
        self._check_source(self._python_interpreter_for_source_on_command_line('exit(0)'),
                           home_and_sds_test.Arrangement(),
                           home_and_sds_test.Expectation(expected_action_result=is_success_result(0,
                                                                                                  None)))

    def test_check_non_zero_exit_code(self):
        self._check_source(self._python_interpreter_for_source_on_command_line('exit(1)'),
                           home_and_sds_test.Arrangement(),
                           home_and_sds_test.Expectation(expected_action_result=is_success_result(1,
                                                                                                  '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write("on stderr"); exit(2)'
        self._check_source(
            self._python_interpreter_for_source_on_command_line(python_program),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=is_success_result(2,
                                                                                   'on stderr')))

    @staticmethod
    def _python_interpreter_for_source_on_command_line(argument: str) -> SingleInstructionParserSource:
        return single_line_source('( %s ) %s %s' % (py_exe.interpreter_that_executes_argument(),
                                                    sut.SOURCE_OPTION,
                                                    argument))


def py_pgm_that_exits_with_value_on_command_line(stderr_output) -> str:
    return """
import sys

sys.stderr.write('{}');
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecuteProgramWithShellArgumentList),
        unittest.makeSuite(TestExecuteInterpret),
        unittest.makeSuite(TestSource),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name',
                                                                            'single line description')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
