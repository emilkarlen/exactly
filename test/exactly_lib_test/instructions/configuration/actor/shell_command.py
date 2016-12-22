import unittest

from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib_test.act_phase_setups.command_line.test_resources import shell_command_source_line_for
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, _check, \
    file_in_home_dir
from exactly_lib_test.test_case.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForShellCommand),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForShellCommand),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForCommandLineActorForShellCommand),
    ])


class _ShellExecutionCheckerHelper:
    def __init__(self, cli_option: str):
        self.cli_option = cli_option

    def apply(self,
              put: unittest.TestCase,
              instruction_argument_source_template: str,
              act_phase_source_lines: list,
              expectation_of_cmd_and_args: va.ValueAssertion,
              home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
              ):
        # ARRANGE #
        instruction_argument_source = instruction_argument_source_template.format(
            actor_option=self.cli_option,
            shell_option=actor_utils.SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD,
        )
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = Arrangement(instruction_argument_source,
                                  act_phase_source_lines,
                                  act_phase_process_executor=os_process_executor,
                                  home_dir_contents=home_dir_contents)
        expectation = Expectation()
        # ACT #
        _check(put, arrangement, expectation)
        # ASSERT #
        put.assertTrue(os_process_executor.command.shell,
                       'Command should indicate shell execution')
        actual_cmd_and_args = os_process_executor.command.args
        put.assertIsInstance(actual_cmd_and_args, str,
                             'Arguments of command to execute should be a string')
        expectation_of_cmd_and_args.apply_with_message(put, actual_cmd_and_args, 'cmd_and_args')


def initial_part_of_command_without_file_argument_is(
        expected_command_except_final_file_name_part: str) -> va.ValueAssertion:
    class RetClass(va.ValueAssertion):
        def apply(self,
                  put: unittest.TestCase,
                  actual_cmd_and_args: str,
                  message_builder: va.MessageBuilder = va.MessageBuilder()):
            put.assertTrue(len(actual_cmd_and_args) > len(expected_command_except_final_file_name_part),
                           'Command line string is expected to contain at least the argument of the instruction')
            command_head = actual_cmd_and_args[:len(expected_command_except_final_file_name_part)]
            put.assertEqual(command_head,
                            expected_command_except_final_file_name_part)

    return RetClass()


class TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForShellCommand(unittest.TestCase):
    helper = _ShellExecutionCheckerHelper(actor_utils.SOURCE_INTERPRETER_OPTION)

    def _check(self, instruction_argument_source_template: str,
               expected_command_except_final_file_name_part: va.ValueAssertion):
        self.helper.apply(self, instruction_argument_source_template,
                          ['this is act phase source code that is not used in the test'],
                          expected_command_except_final_file_name_part)

    def test_single_command(self):
        self._check('{actor_option} {shell_option} arg',
                    initial_part_of_command_without_file_argument_is('arg'))

    def test_command_with_arguments(self):
        self._check('{actor_option} {shell_option} arg arg1 --arg2',
                    initial_part_of_command_without_file_argument_is('arg arg1 --arg2'))

    def test_quoting(self):
        self._check("{actor_option} {shell_option} 'arg with space' arg2 \"arg 3\"",
                    initial_part_of_command_without_file_argument_is("'arg with space' arg2 \"arg 3\""))

    def test_with_interpreter_keyword(self):
        self._check('{actor_option} {shell_option} arg1 arg2',
                    initial_part_of_command_without_file_argument_is('arg1 arg2'))


class TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForShellCommand(unittest.TestCase):
    helper = _ShellExecutionCheckerHelper(actor_utils.FILE_INTERPRETER_OPTION)

    def _check(self, instruction_argument_source_template: str,
               act_phase_source_lines: list,
               expected_command_except_final_file_name_part: va.ValueAssertion,
               home_dir_contents: DirContents,
               ):
        self.helper.apply(self,
                          instruction_argument_source_template,
                          act_phase_source_lines,
                          expected_command_except_final_file_name_part,
                          home_dir_contents)

    def test_single_command(self):
        self._check('{actor_option} {shell_option} arg',
                    ['file.src'],
                    initial_part_of_command_without_file_argument_is('arg'),
                    home_dir_contents=file_in_home_dir('file.src'))

    def test_command_with_arguments(self):
        self._check('{actor_option} {shell_option} arg arg1 --arg2',
                    ['file.src'],
                    initial_part_of_command_without_file_argument_is('arg arg1 --arg2'),
                    home_dir_contents=file_in_home_dir('file.src'))

    def test_quoting(self):
        self._check("{actor_option} {shell_option} 'arg with space' arg2 \"arg 3\"",
                    ['file.src'],
                    initial_part_of_command_without_file_argument_is("'arg with space' arg2 \"arg 3\""),
                    home_dir_contents=file_in_home_dir('file.src'))

    def test_with_interpreter_keyword(self):
        self._check('{actor_option} {shell_option} arg1 arg2',
                    ['file.src'],
                    initial_part_of_command_without_file_argument_is('arg1 arg2'),
                    home_dir_contents=file_in_home_dir('file.src'))


class TestSuccessfulParseAndInstructionExecutionForCommandLineActorForShellCommand(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = Arrangement(actor_utils.COMMAND_LINE_ACTOR_OPTION,
                                  [shell_command_source_line_for('act phase source')],
                                  act_phase_process_executor=os_process_executor)
        expectation = Expectation()
        # ACT #
        _check(self, arrangement, expectation)
        # ASSERT #
        self.assertTrue(os_process_executor.command.shell,
                        'Command should indicate shell execution')
        actual_cmd_and_args = os_process_executor.command.args
        self.assertIsInstance(actual_cmd_and_args, str,
                              'Arguments of command to execute should be a string')
        self.assertEqual(actual_cmd_and_args,
                         'act phase source')
