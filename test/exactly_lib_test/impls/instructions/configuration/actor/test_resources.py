import pathlib
import unittest
from typing import Sequence, Callable, List

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.impls.actors.util import parse_act_interpreter
from exactly_lib.impls.instructions.configuration import actor as sut
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.appl_env.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.impls.actors.test_resources import integration_check, relativity_configurations
from exactly_lib_test.impls.actors.test_resources.integration_check import PostSdsExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_with_assertion
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRaisesImplementationException
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.sequence_assertions import matches_elements_except_last
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command


def shell_command_syntax_for(command: str) -> str:
    return parse_act_interpreter.SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD + ' ' + command


class Arrangement:
    def __init__(self,
                 source: ParseSource,
                 act_phase_source_lines: List[str],
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 ):
        self.hds_contents = hds_contents
        self.source = source
        self.act_phase_source_lines = act_phase_source_lines
        self.os_services = os_services


class Expectation:
    def __init__(self,
                 sub_process_result_from_execute: ValueAssertion[SubProcessResult] = asrt.anything_goes(),
                 source_after_parse: ValueAssertion[ParseSource] = asrt.anything_goes(),
                 symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 after_execution: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
                 ):
        self.sub_process_result_from_execute = sub_process_result_from_execute
        self.source_after_parse = source_after_parse
        self.symbol_usages = symbol_usages
        self.after_execution = after_execution


def check_actor_execution(put: unittest.TestCase,
                          arrangement: Arrangement,
                          expectation: Expectation):
    instruction = sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, arrangement.source)
    configuration_builder = _configuration_builder_with_exception_throwing_act_phase_setup()
    assert isinstance(instruction, ConfigurationPhaseInstruction)
    instruction.main(configuration_builder)
    act_phase_instructions = [instr(arrangement.act_phase_source_lines)]
    integration_check.check_execution(
        put,
        configuration_builder.actor.value,
        act_phase_instructions,
        integration_check.Arrangement(
            hds_contents=arrangement.hds_contents,
            process_execution=ProcessExecutionArrangement(
                os_services=arrangement.os_services,
            )),
        integration_check.Expectation(
            symbol_usages=expectation.symbol_usages,
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=expectation.sub_process_result_from_execute
            ),
            after_execution=expectation.after_execution
        )
    )
    expectation.source_after_parse.apply_with_message(put, arrangement.source, 'source after parse')


def _configuration_builder_with_exception_throwing_act_phase_setup() -> ConfigurationBuilder:
    initial_hds_dir = pathlib.Path()
    return ConfigurationBuilder(initial_hds_dir,
                                initial_hds_dir,
                                NameAndValue('the actor', ActorThatRaisesImplementationException())
                                )


def file_in_hds_act_dir(file_name: str) -> hds_populators.HdsPopulator:
    return hds_populators.contents_in(RelHdsOptionType.REL_HDS_ACT,
                                      fs.DirContents([File.empty(file_name)]))


class ExecutedCommandAssertion(asrt.ValueAssertionBase[TestCaseDs]):
    def __init__(self,
                 command_executor: CommandExecutorThatRecordsArguments,
                 get_command_assertion: Callable[[TestCaseDs], ValueAssertion[Command]],
                 ):
        self.command_executor = command_executor
        self.get_command_assertion = get_command_assertion

    def _apply(self,
               put: unittest.TestCase,
               value: TestCaseDs,
               message_builder: MessageBuilder,
               ):
        command_assertion = self.get_command_assertion(value)
        command_assertion.apply(
            put,
            self.command_executor.command,
            message_builder.for_sub_component('command'),
        )


_ACTOR_OPTION_NAME_IN_INSTRUCTION_ARGUMENT_TEMPLATE = 'actor_option'


class CheckHelper:
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
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]],
            expected_command: Callable[[TestCaseDs], ValueAssertion[Command]],
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
            expectation = Expectation(
                source_after_parse=source_assertion,
                symbol_usages=symbol_usages,
                after_execution=ExecutedCommandAssertion(command_executor, expected_command)
            )
            # ACT & ASSERT #
            check_actor_execution(put, arrangement, expectation)


def equals_with_last_element_removed(expected: list) -> ValueAssertion:
    return asrt.sub_component('all elements except last',
                              lambda l: l[:-1],
                              asrt.Equals(expected))


def exe_file_in_interpreter_default_relativity_dir(file_name: str) -> hds_populators.HdsPopulator:
    return relativity_configurations.INTERPRETER_FILE.populator_for_relativity_option_root__hds(
        fs.DirContents([fs.executable_file(file_name)])
    )


def is_exe_file_command_for_source_file(interpreter_exe_file: str,
                                        source_file_relative_hds_name: str,
                                        arguments: List[str],
                                        ) -> Callable[[TestCaseDs], ValueAssertion[Command]]:
    def ret_val(tcds: TestCaseDs) -> ValueAssertion[Command]:
        return asrt_command.matches_command(
            asrt_command.matches_executable_file_command_driver(
                asrt.equals(tcds.hds.case_dir / interpreter_exe_file)
            ),
            asrt.equals(arguments + [str(tcds.hds.act_dir / source_file_relative_hds_name)])
        )

    return ret_val


def is_exe_file_command_for_source(interpreter_exe_file: str,
                                   arguments: List[str],
                                   ) -> Callable[[TestCaseDs], ValueAssertion[Command]]:
    def ret_val(tcds: TestCaseDs) -> ValueAssertion[Command]:
        return asrt_command.matches_command(
            asrt_command.matches_executable_file_command_driver(
                asrt.equals(tcds.hds.case_dir / interpreter_exe_file)
            ),
            matches_elements_except_last(asrt.equals(arguments))
        )

    return ret_val


def expected_cmd_and_args__const(expected: ValueAssertion[Command]) -> Callable[[TestCaseDs], ValueAssertion[Command]]:
    def ret_val(tcds: TestCaseDs) -> ValueAssertion[Command]:
        return expected

    return ret_val
