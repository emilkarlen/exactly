import pathlib
import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.actor import actor_utils
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.atc_os_proc_executors import DEFAULT_ATC_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType
from exactly_lib_test.actors.test_resources import act_phase_execution
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRaisesImplementationException
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def shell_command_syntax_for(command: str) -> str:
    return actor_utils.SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD + ' ' + command


class Arrangement:
    def __init__(self,
                 source: ParseSource,
                 act_phase_source_lines: list,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 atc_os_process_executor: AtcOsProcessExecutor = DEFAULT_ATC_OS_PROCESS_EXECUTOR
                 ):
        self.hds_contents = hds_contents
        self.source = source
        self.act_phase_source_lines = act_phase_source_lines
        self.atc_os_process_executor = atc_os_process_executor


class Expectation:
    def __init__(self,
                 sub_process_result_from_execute: ValueAssertion = asrt.anything_goes(),
                 source_after_parse: ValueAssertion = asrt.anything_goes()):
        self.sub_process_result_from_execute = sub_process_result_from_execute
        self.source_after_parse = source_after_parse


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation):
    instruction = sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, arrangement.source)
    configuration_builder = _configuration_builder_with_exception_throwing_act_phase_setup()
    assert isinstance(instruction, ConfigurationPhaseInstruction)
    instruction.main(configuration_builder)
    act_phase_instructions = [instr(arrangement.act_phase_source_lines)]
    act_phase_execution.check_execution(put,
                                        configuration_builder.actor,
                                        act_phase_instructions,
                                        act_phase_execution.Arrangement(
                                            hds_contents=arrangement.hds_contents,
                                            atc_process_executor=arrangement.atc_os_process_executor),
                                        act_phase_execution.Expectation(
                                            sub_process_result_from_execute=expectation.sub_process_result_from_execute)
                                        )
    expectation.source_after_parse.apply_with_message(put, arrangement.source, 'source after parse')


def _configuration_builder_with_exception_throwing_act_phase_setup() -> ConfigurationBuilder:
    initial_hds_dir = pathlib.Path()
    return ConfigurationBuilder(initial_hds_dir,
                                initial_hds_dir,
                                ActorThatRaisesImplementationException())


def file_in_hds_act_dir(file_name: str) -> hds_populators.HdsPopulator:
    return hds_populators.contents_in(RelHdsOptionType.REL_HDS_ACT,
                                      fs.DirContents([File.empty(file_name)]))
