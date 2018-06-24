import copy
import pathlib
import unittest
from typing import Callable

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result.sh import SuccessOrHardError
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementBase
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_phase_handlings import dummy_act_phase_handling
from exactly_lib_test.test_case.result.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Arrangement(ArrangementBase):
    def __init__(self,
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 file_ref_rel_root_dir: DirContents = empty_dir_contents(),
                 act_phase_handling: ActPhaseHandling = dummy_act_phase_handling(),
                 execution_mode: ExecutionMode = ExecutionMode.PASS,
                 timeout_in_seconds: int = None):
        super().__init__(hds_contents=hds_contents)
        self.file_ref_rel_root_dir = file_ref_rel_root_dir
        self.act_phase_handling = act_phase_handling
        self.execution_mode = execution_mode
        self.timeout_in_seconds = timeout_in_seconds


class Expectation:
    def __init__(self,
                 main_result: asrt.ValueAssertion[SuccessOrHardError] = sh_assertions.is_success(),
                 configuration: config_check.Assertion = config_check.AnythingGoes(),
                 source: asrt.ValueAssertion[ParseSource] = asrt.anything_goes(),
                 configuration2: asrt.ValueAssertion[ConfigurationBuilder] = asrt.anything_goes(),
                 file_ref_rel_root_2_conf: Callable[[pathlib.Path], asrt.ValueAssertion[ConfigurationBuilder]] =
                 lambda x: asrt.anything_goes()
                 ):
        self.main_result = main_result
        self.configuration = configuration
        self.configuration2 = configuration2
        self.file_ref_rel_root_2_conf = file_ref_rel_root_2_conf
        self.source = source


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: Arrangement,
               expectation: Expectation):
        Executor(self, arrangement, expectation).execute(parser, source)


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self,
                parser: InstructionParser,
                source: ParseSource):
        with tmp_dir(self.arrangement.file_ref_rel_root_dir) as file_ref_rel_root_dir_path:
            fs_location_info = FileSystemLocationInfo(file_ref_rel_root_dir_path)

            instruction = parser.parse(fs_location_info, source)

            self.put.assertIsNotNone(instruction,
                                     'Result from parser cannot be None')
            self.put.assertIsInstance(instruction,
                                      ConfigurationPhaseInstruction,
                                      'The instruction must be an instance of ' + str(ConfigurationPhaseInstruction))
            self.expectation.source.apply_with_message(self.put, source, 'source')

            assert isinstance(instruction, ConfigurationPhaseInstruction)

            with home_directory_structure(contents=self.arrangement.hds_contents) as hds:
                configuration_builder = ConfigurationBuilder(hds.case_dir,
                                                             hds.act_dir,
                                                             self.arrangement.act_phase_handling,
                                                             timeout_in_seconds=self.arrangement.timeout_in_seconds,
                                                             execution_mode=self.arrangement.execution_mode)

                initial_configuration_builder = copy.deepcopy(configuration_builder)

                self._execute_main(configuration_builder, instruction)

                self.expectation.configuration2.apply_with_message(self.put,
                                                                   configuration_builder,
                                                                   'ConfigurationBuilder')

                self.expectation.configuration.apply(self.put,
                                                     initial_configuration_builder,
                                                     configuration_builder)

                self.expectation.file_ref_rel_root_2_conf(
                    file_ref_rel_root_dir_path
                ).apply_with_message(self.put,
                                     configuration_builder,
                                     'ConfigurationBuilder with file-ref-rel-root-dir')

    def _execute_main(self,
                      configuration_builder: ConfigurationBuilder,
                      instruction: ConfigurationPhaseInstruction):
        main_result = instruction.main(configuration_builder)
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply_with_message(self.put, main_result,
                                                        'result of main')
