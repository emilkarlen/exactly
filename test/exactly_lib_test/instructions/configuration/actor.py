import pathlib
import sys
import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActSourceAndExecutorConstructor, \
    ActPhaseOsProcessExecutor
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.act_phase_setups.command_line.test_resources import shell_command_source_line_for
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure import empty_file
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseForAnyActor),
        unittest.makeSuite(TestFailingParseForCommandLine),
        unittest.makeSuite(TestFailingParseForInterpreter),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForFileInterpreterActor),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActor),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForShellCommandInterpreterActor),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForCommandLineActorForExecutableFile),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForCommandLineActorForShellCommand),
        unittest.makeSuite(TestShellHandlingViaExecution),
        suite_for_instruction_documentation(sut.setup('instruction name').documentation),
    ])


class TestFailingParseForAnyActor(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_the_quoting_is_invalid(self):
        source = new_source2('argument-1 "argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestFailingParseForCommandLine(unittest.TestCase):
    def test_fail_when_extra_unexpected_argument(self):
        source = new_source2(actor_utils.COMMAND_LINE_ACTOR_OPTION + ' extra-unexpected-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestFailingParseForInterpreter(unittest.TestCase):
    def test_fail_when_missing_program_argument(self):
        source = new_source2(actor_utils.SOURCE_INTERPRETER_OPTION)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class _NonShellExecutionCheckHelper:
    def __init__(self, cli_option: str):
        self.cli_option = cli_option

    def apply(self, put: unittest.TestCase,
              instruction_argument_source_template: str,
              act_phase_source_lines: list,
              expected_cmd_and_args: va.ValueAssertion,
              home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
              ):
        # ARRANGE #
        instruction_argument_source = instruction_argument_source_template.format(
            actor_option=self.cli_option)
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = Arrangement(instruction_argument_source,
                                  act_phase_source_lines,
                                  act_phase_process_executor=os_process_executor,
                                  home_dir_contents=home_dir_contents)
        expectation = Expectation()
        # ACT #
        _check(put, arrangement, expectation)
        # ASSERT #
        put.assertFalse(os_process_executor.command.shell,
                        'Command should not indicate shell execution')
        actual_cmd_and_args = os_process_executor.command.args
        put.assertIsInstance(actual_cmd_and_args, list,
                             'Arguments of command to execute should be a list of arguments')
        put.assertTrue(len(actual_cmd_and_args) > 0,
                       'List of arguments is expected to contain at least the file|interpreter argument')
        expected_cmd_and_args.apply_with_message(put, actual_cmd_and_args, 'actual_cmd_and_args')


def equals_with_last_element_removed(expected: list) -> va.ValueAssertion:
    return va.sub_component('all elements except last',
                            lambda l: l[:-1],
                            va.Equals(expected))


class TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActor(unittest.TestCase):
    helper = _NonShellExecutionCheckHelper(actor_utils.SOURCE_INTERPRETER_OPTION)

    def _check(self, instruction_argument_source_template: str,
               expected_command_and_arguments_except_final_file_name_arg: list):
        self.helper.apply(self,
                          instruction_argument_source_template,
                          act_phase_source_lines=['this is act phase source code that is not used in the test'],
                          expected_cmd_and_args=equals_with_last_element_removed(
                              expected_command_and_arguments_except_final_file_name_arg),
                          )

    def test_single_command(self):
        self._check('{actor_option} executable', ['executable'])

    def test_command_with_arguments(self):
        self._check('{actor_option} executable arg1 --arg2',
                    ['executable', 'arg1', '--arg2'])

    def test_quoting(self):
        self._check("{actor_option} 'executable with space' arg2 \"arg 3\"",
                    ['executable with space', 'arg2', 'arg 3'])


class TestSuccessfulParseAndInstructionExecutionForFileInterpreterActor(unittest.TestCase):
    helper = _NonShellExecutionCheckHelper(actor_utils.FILE_INTERPRETER_OPTION)

    def _check(self, instruction_argument_source_template: str,
               act_phase_source_lines: list,
               cmd_and_args: va.ValueAssertion,
               home_dir_contents: file_structure.DirContents = file_structure.DirContents([])):
        self.helper.apply(self,
                          instruction_argument_source_template,
                          act_phase_source_lines=act_phase_source_lines,
                          expected_cmd_and_args=cmd_and_args,
                          home_dir_contents=home_dir_contents)

    def test_single_command(self):
        self._check('{actor_option} interpreter',
                    ['file.src'],
                    is_interpreter_with_source_file_and_arguments('interpreter',
                                                                  'file.src',
                                                                  []),
                    home_dir_contents=file_in_home_dir('file.src'))

    def test_command_with_arguments(self):
        self._check('{actor_option}   interpreter   arg1     --arg2   ',
                    ['file.src'],
                    is_interpreter_with_source_file_and_arguments('interpreter',
                                                                  'file.src',
                                                                  ['arg1', '--arg2']),
                    home_dir_contents=file_in_home_dir('file.src')
                    )

    def test_quoting(self):
        self._check("{actor_option} 'interpreter with space' arg2 \"arg 3\"",
                    ['file.src'],
                    is_interpreter_with_source_file_and_arguments('interpreter with space',
                                                                  'file.src',
                                                                  ['arg2', 'arg 3']),
                    home_dir_contents=file_in_home_dir('file.src')
                    )


def file_in_home_dir(file_name: str) -> file_structure.DirContents:
    return file_structure.DirContents([empty_file(file_name)])


def is_interpreter_with_source_file_and_arguments(interpreter: str,
                                                  source_file_relative_home_name: str,
                                                  arguments: list) -> va.ValueAssertion:
    class RetClass(va.ValueAssertion):
        def apply(self,
                  put: unittest.TestCase,
                  cmd_and_args: list,
                  message_builder: va.MessageBuilder = va.MessageBuilder()):
            msg = 'Expecting cmd-and-args to be [interpreter, argument..., source-file]. Found: ' + str(
                cmd_and_args)
            put.assertEquals(1 + 1 + len(arguments), len(cmd_and_args),
                             msg)
            put.assertEqual(interpreter, cmd_and_args[0], 'First element should be the interpreter')
            put.assertEqual(arguments, cmd_and_args[1:-1], 'Interpreter arguments')

    return RetClass()


class TestSuccessfulParseAndInstructionExecutionForShellCommandInterpreterActor(unittest.TestCase):
    def _check(self, instruction_argument_source_template: str,
               expected_command_except_final_file_name_part: str):
        # ARRANGE #
        instruction_argument_source = instruction_argument_source_template.format(
            actor_option=actor_utils.SOURCE_INTERPRETER_OPTION,
            shell_option=actor_utils.SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD,
        )
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = Arrangement(instruction_argument_source,
                                  ['this is act phase source code that is not used in the test'],
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
        self.assertTrue(len(actual_cmd_and_args) > len(expected_command_except_final_file_name_part),
                        'Command line string is expected to contain at least the argument of the instruction')
        command_head = actual_cmd_and_args[:len(expected_command_except_final_file_name_part)]
        self.assertEqual(command_head,
                         expected_command_except_final_file_name_part)

    def test_single_command(self):
        self._check('{actor_option} {shell_option} arg', 'arg')

    def test_command_with_arguments(self):
        self._check('{actor_option} {shell_option} arg arg1 --arg2',
                    'arg arg1 --arg2')

    def test_quoting(self):
        self._check("{actor_option} {shell_option} 'arg with space' arg2 \"arg 3\"",
                    "'arg with space' arg2 \"arg 3\"")

    def test_with_interpreter_keyword(self):
        self._check('{actor_option} {shell_option} arg1 arg2',
                    'arg1 arg2')


class TestSuccessfulParseAndInstructionExecutionForCommandLineActorForExecutableFile(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        executable_file = sys.executable
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = Arrangement(actor_utils.COMMAND_LINE_ACTOR_OPTION,
                                  [executable_file],
                                  act_phase_process_executor=os_process_executor)
        expectation = Expectation()
        # ACT #
        _check(self, arrangement, expectation)
        # ASSERT #
        self.assertFalse(os_process_executor.command.shell,
                         'Command should indicate executable file execution')
        actual_cmd_and_args = os_process_executor.command.args
        self.assertIsInstance(actual_cmd_and_args, list,
                              'Arguments of command to execute should be a list')
        self.assertListEqual([executable_file],
                             actual_cmd_and_args)


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


class TestShellHandlingViaExecution(unittest.TestCase):
    def test_valid_shell_command(self):
        act_phase_source_line = shell_command_source_line_for(
            shell_commands.command_that_prints_line_to_stdout('output on stdout'))
        _check(self,
               Arrangement(actor_utils.COMMAND_LINE_ACTOR_OPTION,
                           [act_phase_source_line]),
               Expectation(sub_process_result_from_execute=pr.stdout(va.Equals('output on stdout\n',
                                                                               'expected output on stdout')))
               )


class Arrangement:
    def __init__(self,
                 instruction_argument: str,
                 act_phase_source_lines: list,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 act_phase_process_executor: ActPhaseOsProcessExecutor = ACT_PHASE_OS_PROCESS_EXECUTOR
                 ):
        self.home_dir_contents = home_dir_contents
        self.instruction_argument = instruction_argument
        self.act_phase_source_lines = act_phase_source_lines
        self.act_phase_process_executor = act_phase_process_executor


class Expectation:
    def __init__(self,
                 sub_process_result_from_execute: va.ValueAssertion = va.anything_goes()):
        self.sub_process_result_from_execute = sub_process_result_from_execute


def _check(put: unittest.TestCase,
           arrangement: Arrangement,
           expectation: Expectation):
    source = new_source2(arrangement.instruction_argument)
    instruction = sut.Parser().apply(source)
    configuration_builder = _configuration_builder_with_exception_throwing_act_phase_setup()
    instruction.main(configuration_builder)
    act_phase_instructions = [instr(arrangement.act_phase_source_lines)]
    executor_constructor = configuration_builder.act_phase_handling.source_and_executor_constructor
    act_phase_execution.check_execution(put,
                                        act_phase_execution.Arrangement(
                                            home_dir_contents=arrangement.home_dir_contents,
                                            executor_constructor=executor_constructor,
                                            act_phase_instructions=act_phase_instructions,
                                            act_phase_process_executor=arrangement.act_phase_process_executor),
                                        act_phase_execution.Expectation(
                                            sub_process_result_from_execute=expectation.sub_process_result_from_execute)
                                        )


def _configuration_builder_with_exception_throwing_act_phase_setup() -> ConfigurationBuilder:
    return ConfigurationBuilder(pathlib.Path(),
                                ActPhaseHandling(_ActSourceAndExecutorConstructorThatRaisesException()))


class _ActSourceAndExecutorConstructorThatRaisesException(ActSourceAndExecutorConstructor):
    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list):
        raise ValueError('the method should never be called')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
