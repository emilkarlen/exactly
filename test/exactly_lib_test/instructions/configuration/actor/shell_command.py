import unittest
from typing import List

from exactly_lib.actors.util import parse_act_interpreter
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, check, \
    file_in_hds_act_dir, shell_command_syntax_for
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources import command_assertions as asrt_command
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_with_assertion
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, \
    value_assertion_str as asrt_str, \
    shlex_assertions as asrt_shlex, \
    process_result_assertions as asrt_proc_result, \
    file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForShellCommand),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForShellCommand),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForCommandLineActorForShellCommand),
        unittest.makeSuite(TestShellHandlingViaExecution),
    ])


class _ShellExecutionCheckerHelper:
    def __init__(self, cli_option: str):
        self.cli_option = cli_option

    def apply(self,
              put: unittest.TestCase,
              instruction_argument_source_template: str,
              act_phase_source_lines: List[str],
              expected_command: ValueAssertion[Command],
              hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
              ):
        instruction_argument_source = instruction_argument_source_template.format(
            actor_option=self.cli_option,
            shell_option=parse_act_interpreter.SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD,
        )
        for source, source_assertion in equivalent_source_variants_with_assertion(put, instruction_argument_source):
            # ARRANGE #
            command_executor = CommandExecutorThatRecordsArguments()
            arrangement = Arrangement(
                source=source,
                act_phase_source_lines=act_phase_source_lines,
                hds_contents=hds_contents,
                os_services=os_services_access.new_for_cmd_exe(command_executor),
            )
            expectation = Expectation(source_after_parse=source_assertion)
            # ACT #
            check(put, arrangement, expectation)
            # ASSERT #
            expected_command.apply_with_message(
                put,
                command_executor.command,
                'command',
            )


def initial_part_of_command_without_file_argument_is(
        expected_command_except_final_file_name_part: str) -> ValueAssertion[Command]:
    return asrt_command.matches_command(
        driver=asrt_command.matches_shell_command_driver(
            asrt_str.begins_with(expected_command_except_final_file_name_part)
        ),
        arguments=asrt.is_empty_sequence
    )


def shell_command_is(
        expected_command: str,
        src_file_nam: str,
        additional_arguments: List[str],
) -> ValueAssertion[Command]:
    arguments = [
        asrt_shlex.matches_single_quotes_str(
            asrt_path.str_as_path(asrt_path.name_equals(src_file_nam))
        )
    ]
    arguments += [
        asrt.equals(arg_string)
        for arg_string in additional_arguments
    ]
    return asrt_command.matches_command(
        driver=asrt_command.matches_shell_command_driver(
            asrt.equals(expected_command)
        ),
        arguments=asrt.matches_sequence(arguments)
    )


class TestSuccessfulParseAndInstructionExecutionForSourceInterpreterActorForShellCommand(unittest.TestCase):
    helper = _ShellExecutionCheckerHelper(actor_utils.SOURCE_INTERPRETER_OPTION)

    def _check(self,
               instruction_argument_source_template: str,
               expected_command_except_final_file_name_part: ValueAssertion[Command],
               ):
        self.helper.apply(self, instruction_argument_source_template,
                          ['this is act phase source code that is not used in the test'],
                          expected_command_except_final_file_name_part)

    def test_single_command(self):
        self._check('= {actor_option} {shell_option} arg',
                    initial_part_of_command_without_file_argument_is('arg'))

    def test_command_with_arguments(self):
        self._check(' = {actor_option} {shell_option} arg arg1 -arg2',
                    initial_part_of_command_without_file_argument_is('arg arg1 -arg2'))

    def test_quoting(self):
        self._check("  =  {actor_option} {shell_option} 'arg with space' arg2 \"arg 3\"",
                    initial_part_of_command_without_file_argument_is("'arg with space' arg2 \"arg 3\""))


class TestSuccessfulParseAndInstructionExecutionForFileInterpreterActorForShellCommand(unittest.TestCase):
    helper = _ShellExecutionCheckerHelper(actor_utils.FILE_INTERPRETER_OPTION)

    def _check(self,
               instruction_argument_source_template: str,
               act_phase_source_lines: List[str],
               expected_command_except_final_file_name_part: ValueAssertion,
               hds_contents: hds_populators.HdsPopulator,
               ):
        self.helper.apply(self,
                          instruction_argument_source_template,
                          act_phase_source_lines,
                          expected_command_except_final_file_name_part,
                          hds_contents)

    def test_single_command(self):
        self._check('= {actor_option} {shell_option} interpreter',
                    ['file.src'],
                    shell_command_is('interpreter',
                                     'file.src',
                                     ['']),
                    hds_contents=file_in_hds_act_dir('file.src'))

    def test_command_with_arguments(self):
        self._check(' = {actor_option} {shell_option} interpreter with -arg2',
                    ['file.src'],
                    shell_command_is('interpreter with -arg2',
                                     'file.src',
                                     ['']),
                    hds_contents=file_in_hds_act_dir('file.src'))

    def test_quoting(self):
        self._check(" = {actor_option} {shell_option} 'interpreter with quoting' arg2 \"arg 3\"",
                    ['file.src'],
                    shell_command_is("'interpreter with quoting' arg2 \"arg 3\"",
                                     'file.src',
                                     ['']),
                    hds_contents=file_in_hds_act_dir('file.src'))


class TestSuccessfulParseAndInstructionExecutionForCommandLineActorForShellCommand(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        command_executor = CommandExecutorThatRecordsArguments()
        act_phase_source = 'act phase source'

        arrangement = Arrangement(
            source=remaining_source('= ' + actor_utils.COMMAND_LINE_ACTOR_OPTION),
            act_phase_source_lines=[shell_command_syntax_for(act_phase_source)],
            os_services=os_services_access.new_for_cmd_exe(command_executor),
        )
        expectation = Expectation()
        # ACT #
        check(self, arrangement, expectation)
        # ASSERT #
        expected_command = asrt_command.matches_command(
            driver=asrt_command.matches_shell_command_driver(
                asrt.equals(act_phase_source)
            ),
            arguments=asrt.is_empty_sequence
        )
        expected_command.apply_with_message(
            self,
            command_executor.command,
            'command',
        )


class TestShellHandlingViaExecution(unittest.TestCase):
    def test_valid_shell_command(self):
        act_phase_source_line = shell_command_syntax_for(
            shell_commands.command_that_prints_line_to_stdout('output on stdout'))
        check(self,
              Arrangement(
                  source=remaining_source('= ' + actor_utils.COMMAND_LINE_ACTOR_OPTION),
                  act_phase_source_lines=[act_phase_source_line]),
              Expectation(
                  sub_process_result_from_execute=asrt_proc_result.stdout(
                      asrt.Equals('output on stdout\n'))
              )
              )
