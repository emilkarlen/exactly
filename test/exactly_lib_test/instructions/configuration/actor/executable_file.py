import sys
import unittest

from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, check, \
    file_in_home_act_dir
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.actor.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_with_assertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForExecutableFile),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForExecutableFIle),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForCommandLineActorForExecutableFile),
    ])


_ACTOR_OPTION_NAME_IN_INSTRUCTION_ARGUMENT_TEMPLATE = 'actor_option'


class _NonShellExecutionCheckHelper:
    def __init__(self, cli_option: str):
        self.cli_option = cli_option
        self.format_map_for_template_string = {
            _ACTOR_OPTION_NAME_IN_INSTRUCTION_ARGUMENT_TEMPLATE: self.cli_option
        }

    def check_both_single_and_multiple_line_source(
            self,
            put: unittest.TestCase,
            first_source_line_instruction_argument_source_template: str,
            act_phase_source_lines: list,
            expected_cmd_and_args: ValueAssertion,
            hds_contents: home_populators.HomePopulator = home_populators.empty()):
        instruction_argument_source = first_source_line_instruction_argument_source_template.format_map(
            self.format_map_for_template_string)
        for source, source_assertion in equivalent_source_variants_with_assertion(put, instruction_argument_source):
            # ARRANGE #
            os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
            arrangement = Arrangement(source,
                                      act_phase_source_lines,
                                      act_phase_process_executor=os_process_executor,
                                      hds_contents=hds_contents)
            expectation = Expectation(source_after_parse=source_assertion)
            # ACT #
            check(put, arrangement, expectation)
            # ASSERT #
            put.assertFalse(os_process_executor.command.shell,
                            'Command should not indicate shell execution')
            actual_cmd_and_args = os_process_executor.command.args
            put.assertIsInstance(actual_cmd_and_args, list,
                                 'Arguments of command to execute should be a list of arguments')
            put.assertTrue(len(actual_cmd_and_args) > 0,
                           'List of arguments is expected to contain at least the file|interpreter argument')
            expected_cmd_and_args.apply_with_message(put, actual_cmd_and_args, 'actual_cmd_and_args')


def equals_with_last_element_removed(expected: list) -> ValueAssertion:
    return asrt.sub_component('all elements except last',
                              lambda l: l[:-1],
                              asrt.Equals(expected))


class TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForExecutableFIle(unittest.TestCase):
    helper = _NonShellExecutionCheckHelper(actor_utils.SOURCE_INTERPRETER_OPTION)

    def _check_both_single_and_multiple_line_source(self,
                                                    instruction_argument_source_template: str,
                                                    expected_command_and_arguments_except_final_file_name_arg: list):
        self.helper.check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template,
            act_phase_source_lines=['this is act phase source code that is not used in the test'],
            expected_cmd_and_args=equals_with_last_element_removed(
                expected_command_and_arguments_except_final_file_name_arg),
        )

    def test_single_command(self):
        self._check_both_single_and_multiple_line_source(
            ' = {actor_option} executable', ['executable'])

    def test_command_with_arguments(self):
        self._check_both_single_and_multiple_line_source(
            '=  {actor_option} executable arg1 -arg2',
            ['executable', 'arg1', '-arg2'])

    def test_quoting(self):
        self._check_both_single_and_multiple_line_source(
            "= {actor_option} 'executable with space' arg2 \"arg 3\"",
            ['executable with space', 'arg2', 'arg 3'])


class TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForExecutableFile(unittest.TestCase):
    helper = _NonShellExecutionCheckHelper(actor_utils.FILE_INTERPRETER_OPTION)

    def _check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template: str,
            act_phase_source_lines: list,
            cmd_and_args: ValueAssertion,
            hds_contents: home_populators.HomePopulator = home_populators.empty()):
        self.helper.check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template,
            act_phase_source_lines=act_phase_source_lines,
            expected_cmd_and_args=cmd_and_args,
            hds_contents=hds_contents)

    def test_single_command(self):
        self._check_both_single_and_multiple_line_source(
            '= {actor_option} interpreter',
            ['file.src'],
            is_interpreter_with_source_file_and_arguments('interpreter',
                                                          'file.src',
                                                          []),
            hds_contents=file_in_home_act_dir('file.src'))

    def test_command_with_arguments(self):
        self._check_both_single_and_multiple_line_source(
            ' = {actor_option}   interpreter   arg1     -arg2   ',
            ['file.src'],
            is_interpreter_with_source_file_and_arguments('interpreter',
                                                          'file.src',
                                                          ['arg1',
                                                           '-arg2']),
            hds_contents=file_in_home_act_dir('file.src')
        )

    def test_quoting(self):
        self._check_both_single_and_multiple_line_source(
            "= {actor_option} 'interpreter with space' arg2 \"arg 3\"",
            ['file.src'],
            is_interpreter_with_source_file_and_arguments(
                'interpreter with space',
                'file.src',
                ['arg2', 'arg 3']),
            hds_contents=file_in_home_act_dir('file.src')
        )


def is_interpreter_with_source_file_and_arguments(interpreter: str,
                                                  source_file_relative_home_name: str,
                                                  arguments: list) -> ValueAssertion:
    class RetClass(ValueAssertionBase):
        def _apply(self,
                   put: unittest.TestCase,
                   cmd_and_args: list,
                   message_builder: asrt.MessageBuilder):
            msg = 'Expecting cmd-and-args to be [interpreter, argument..., source-file]. Found: ' + str(
                cmd_and_args)
            put.assertEqual(1 + 1 + len(arguments), len(cmd_and_args),
                            msg)
            put.assertEqual(interpreter, cmd_and_args[0], 'First element should be the interpreter')
            put.assertEqual(arguments, cmd_and_args[1:-1], 'Interpreter arguments')

    return RetClass()


class TestSuccessfulParseAndInstructionExecutionForCommandLineActorForExecutableFile(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        executable_file = sys.executable
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = Arrangement(source=remaining_source('= ' + actor_utils.COMMAND_LINE_ACTOR_OPTION),
                                  act_phase_source_lines=[executable_file],
                                  act_phase_process_executor=os_process_executor)
        expectation = Expectation()
        # ACT #
        check(self, arrangement, expectation)
        # ASSERT #
        self.assertFalse(os_process_executor.command.shell,
                         'Command should indicate executable file execution')
        actual_cmd_and_args = os_process_executor.command.args
        self.assertIsInstance(actual_cmd_and_args, list,
                              'Arguments of command to execute should be a list')
        self.assertListEqual([executable_file],
                             actual_cmd_and_args)
