import pathlib
import unittest
from typing import Callable

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileLocationInfo, FileSystemLocationInfo
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result.svh import SuccessOrValidationErrorOrHardError
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case.actor.test_resources.actors import dummy_actor
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementBase
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Arrangement(ArrangementBase):
    def __init__(self,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 root_dir_contents: DirContents = empty_dir_contents(),
                 actor: Actor = dummy_actor(),
                 test_case_status: TestCaseStatus = TestCaseStatus.PASS,
                 timeout_in_seconds: int = None):
        super().__init__(hds_contents=hds_contents)
        self.root_dir_contents = root_dir_contents
        self.actor = actor
        self.test_case_status = test_case_status


class Expectation:
    def __init__(self,
                 main_result: Assertion[SuccessOrValidationErrorOrHardError] = svh_assertions.is_success(),
                 source: Assertion[ParseSource] = asrt.anything_goes(),
                 configuration: Assertion[ConfigurationBuilder] = asrt.anything_goes(),
                 path_rel_root_2_conf: Callable[[pathlib.Path], Assertion[ConfigurationBuilder]] =
                 lambda x: asrt.anything_goes()
                 ):
        self.main_result = main_result
        self.configuration = configuration
        self.path_rel_root_2_conf = path_rel_root_2_conf
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
        with tmp_dir(self.arrangement.root_dir_contents) as abs_path_of_dir_containing_root_file:
            fs_location_info = FileSystemLocationInfo(FileLocationInfo(
                abs_path_of_dir_containing_root_file))

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
                                                             NameAndValue('the actor', self.arrangement.actor),
                                                             test_case_status=self.arrangement.test_case_status)

                self._execute_main(configuration_builder, instruction)

                self.expectation.configuration.apply_with_message(self.put,
                                                                  configuration_builder,
                                                                  'ConfigurationBuilder')

                self.expectation.path_rel_root_2_conf(
                    abs_path_of_dir_containing_root_file
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
