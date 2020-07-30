import sys
import unittest
from typing import List

from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, check, \
    file_in_hds_act_dir
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources import command_assertions as asrt_command
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_with_assertion
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.sequence_assertions import matches_elements_except_last
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
            act_phase_source_lines: List[str],
            expected_cmd_and_args: ValueAssertion[Command],
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
    ):
        instruction_argument_source = first_source_line_instruction_argument_source_template.format_map(
            self.format_map_for_template_string)
        for source, source_assertion in equivalent_source_variants_with_assertion(put, instruction_argument_source):
            # ARRANGE #
            command_executor = CommandExecutorThatRecordsArguments()
            arrangement = Arrangement(
                source,
                act_phase_source_lines,
                os_services=os_services_access.new_for_cmd_exe(command_executor),
                hds_contents=hds_contents,
            )
            expectation = Expectation(source_after_parse=source_assertion)
            # ACT #
            check(put, arrangement, expectation)
            # ASSERT #
            expected_cmd_and_args.apply_with_message(put,
                                                     command_executor.command,
                                                     'command')


def equals_with_last_element_removed(expected: list) -> ValueAssertion:
    return asrt.sub_component('all elements except last',
                              lambda l: l[:-1],
                              asrt.Equals(expected))


class TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForExecutableFIle(unittest.TestCase):
    helper = _NonShellExecutionCheckHelper(actor_utils.SOURCE_INTERPRETER_OPTION)

    def _check_both_single_and_multiple_line_source(self,
                                                    instruction_argument_source_template: str,
                                                    expected_executable: str,
                                                    expected_arguments_except_final_file_name_arg: List[str],
                                                    ):
        self.helper.check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template,
            act_phase_source_lines=['this is act phase source code that is not used in the test'],
            expected_cmd_and_args=asrt_command.matches_command2(
                asrt_command.matches_system_program_command_driver(
                    asrt.equals(expected_executable)
                ),
                matches_elements_except_last(asrt.equals(expected_arguments_except_final_file_name_arg))
            ),
        )

    def test_single_command(self):
        self._check_both_single_and_multiple_line_source(
            ' = {actor_option} executable',
            'executable',
            [],
        )

    def test_command_with_arguments(self):
        self._check_both_single_and_multiple_line_source(
            '=  {actor_option} executable arg1 -arg2',
            'executable',
            ['arg1', '-arg2'])

    def test_quoting(self):
        self._check_both_single_and_multiple_line_source(
            "= {actor_option} 'executable with space' arg2 \"arg 3\"",
            'executable with space',
            ['arg2', 'arg 3'])


class TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForExecutableFile(unittest.TestCase):
    helper = _NonShellExecutionCheckHelper(actor_utils.FILE_INTERPRETER_OPTION)

    def _check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template: str,
            act_phase_source_lines: List[str],
            cmd_and_args: ValueAssertion[Command],
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty()):
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
            hds_contents=file_in_hds_act_dir('file.src'))

    def test_command_with_arguments(self):
        self._check_both_single_and_multiple_line_source(
            ' = {actor_option}   interpreter   arg1     -arg2   ',
            ['file.src'],
            is_interpreter_with_source_file_and_arguments('interpreter',
                                                          'file.src',
                                                          ['arg1',
                                                           '-arg2']),
            hds_contents=file_in_hds_act_dir('file.src')
        )

    def test_quoting(self):
        self._check_both_single_and_multiple_line_source(
            "= {actor_option} 'interpreter with space' arg2 \"arg 3\"",
            ['file.src'],
            is_interpreter_with_source_file_and_arguments(
                'interpreter with space',
                'file.src',
                ['arg2', 'arg 3']),
            hds_contents=file_in_hds_act_dir('file.src')
        )


def is_interpreter_with_source_file_and_arguments(interpreter: str,
                                                  source_file_relative_hds_name: str,
                                                  arguments: List[str],
                                                  ) -> ValueAssertion[Command]:
    return asrt_command.matches_command2(
        asrt_command.matches_system_program_command_driver(
            asrt.equals(interpreter)
        ),
        matches_elements_except_last(asrt.equals(arguments))
    )


class TestSuccessfulParseAndInstructionExecutionForCommandLineActorForExecutableFile(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        executable_file = sys.executable
        command_executor = CommandExecutorThatRecordsArguments()
        arrangement = Arrangement(
            source=remaining_source('= ' + actor_utils.COMMAND_LINE_ACTOR_OPTION),
            act_phase_source_lines=[executable_file],
            os_services=os_services_access.new_for_cmd_exe(command_executor),
        )
        expectation = Expectation()
        # ACT #
        check(self, arrangement, expectation)
        # ASSERT #
        expected_command = asrt_command.matches_command2(
            driver=asrt_command.matches_executable_file_command_driver(
                asrt_path.path_as_str(asrt.equals(executable_file)),
            ),
            arguments=asrt.is_empty_sequence
        )
        expected_command.apply_with_message(
            self,
            command_executor.command,
            'command'
        )
