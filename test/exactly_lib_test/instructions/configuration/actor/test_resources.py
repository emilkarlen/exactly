import pathlib
import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.actor import actor_utils
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor, ActPhaseHandling, \
    ActSourceAndExecutorConstructor
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure import empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def shell_command_syntax_for(command: str) -> str:
    return actor_utils.SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD + ' ' + command


class Arrangement:
    def __init__(self,
                 source: ParseSource,
                 act_phase_source_lines: list,
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 act_phase_process_executor: ActPhaseOsProcessExecutor = ACT_PHASE_OS_PROCESS_EXECUTOR
                 ):
        self.hds_contents = hds_contents
        self.source = source
        self.act_phase_source_lines = act_phase_source_lines
        self.act_phase_process_executor = act_phase_process_executor


class Expectation:
    def __init__(self,
                 sub_process_result_from_execute: asrt.ValueAssertion = asrt.anything_goes(),
                 source_after_parse: asrt.ValueAssertion = asrt.anything_goes()):
        self.sub_process_result_from_execute = sub_process_result_from_execute
        self.source_after_parse = source_after_parse


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation):
    instruction = sut.Parser().parse(arrangement.source)
    configuration_builder = _configuration_builder_with_exception_throwing_act_phase_setup()
    assert isinstance(instruction, ConfigurationPhaseInstruction)
    instruction.main(configuration_builder)
    act_phase_instructions = [instr(arrangement.act_phase_source_lines)]
    executor_constructor = configuration_builder.act_phase_handling.source_and_executor_constructor
    act_phase_execution.check_execution(put,
                                        executor_constructor,
                                        act_phase_instructions,
                                        act_phase_execution.Arrangement(
                                            hds_contents=arrangement.hds_contents,
                                            act_phase_process_executor=arrangement.act_phase_process_executor),
                                        act_phase_execution.Expectation(
                                            sub_process_result_from_execute=expectation.sub_process_result_from_execute)
                                        )
    expectation.source_after_parse.apply_with_message(put, arrangement.source, 'source after parse')


def _configuration_builder_with_exception_throwing_act_phase_setup() -> ConfigurationBuilder:
    initial_home_dir = pathlib.Path()
    return ConfigurationBuilder(initial_home_dir,
                                initial_home_dir,
                                ActPhaseHandling(_ActSourceAndExecutorConstructorThatRaisesException()))


class _ActSourceAndExecutorConstructorThatRaisesException(ActSourceAndExecutorConstructor):
    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list):
        raise ValueError('the method should never be called')


def file_in_home_dir(file_name: str) -> file_structure.DirContents:
    return file_structure.DirContents([empty_file(file_name)])
