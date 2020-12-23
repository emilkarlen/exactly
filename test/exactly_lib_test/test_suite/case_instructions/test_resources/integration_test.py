import unittest
from enum import Enum
from pathlib import Path
from typing import List, Dict, Callable, Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.processing import processors
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_suite import processing as sut, enumeration
from exactly_lib.test_suite.file_reading import suite_hierarchy_reading
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.test_suite.processing import TestCaseProcessorConstructor
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.processing.test_resources.test_case_setup import setup_with_null_act_phase_and_null_preprocessing
from exactly_lib_test.section_document.test_resources.element_parsers import \
    SectionElementParserThatRaisesUnrecognizedSectionElementSourceError
from exactly_lib_test.section_document.test_resources.misc import space_separator_instruction_name_extractor
from exactly_lib_test.section_document.test_resources.source_location_assertions import matches_file_location_info
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.files.str_std_out_files import null_output_reporting_environment
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.test_suite.test_resources.list_recording_instructions import \
    instruction_setup_with_single_phase_with_single_recording_instruction, Recording, matches_recording
from exactly_lib_test.test_suite.test_resources.suite_reporting import ProcessingReporterThatDoesNothing

REGISTER_INSTRUCTION_NAME = 'register'
INSTRUCTION_MARKER_IN_CONTAINING_SUITE = 'containing suite'
INSTRUCTION_MARKER_IN_NON_CONTAINING_SUITE = 'non-containing suite'
INSTRUCTION_MARKER_IN_CASE_1 = 'case 1'
INSTRUCTION_MARKER_IN_CASE_2 = 'case 2'

SUITE_WITH_SYNTAX_ERROR_IN_CASE_PHASE = """\
{case_phase_header}
phase contents causing syntax error
"""

CASE_THAT_REGISTERS_MARKER = """\
{case_phase_header}
{phase_contents_line_that_records}
"""

SUITE_WITH_PHASE_INSTRUCTION_AND_CASES = """\
[cases]

{case_1_file}
{case_2_file}

{case_phase_header}
{phase_contents_line_that_records}
"""

SUITE_WITH_PHASE_INSTRUCTION_BUT_WITH_JUST_A_SUITE = """\
[suites]

{sub_suite_file_name}

{case_phase_header}
{phase_contents_line_that_records}
"""


class InstructionsSequencing(Enum):
    SUITE_BEFORE_CASE = 1
    CASE_BEFORE_SUITE = 2


class PhaseConfig:
    def phase_name(self) -> SectionName:
        raise NotImplementedError('abstract method')

    def instructions_setup(self,
                           register_instruction_name: str,
                           recording_media: List[Recording]) -> InstructionsSetup:
        raise NotImplementedError('abstract method')

    def act_phase_parser(self) -> SectionElementParser:
        raise NotImplementedError('abstract method')

    def actor(self, recording_media: List[Recording]) -> Actor:
        return ActorThatRunsConstantActions()

    def phase_contents_line_that_registers(self,
                                           marker_to_register: str) -> str:
        raise NotImplementedError('abstract method')


class PhaseConfigForPhaseWithInstructions(PhaseConfig):
    def phase_contents_line_that_registers(self,
                                           marker_to_register: str) -> str:
        return REGISTER_INSTRUCTION_NAME + ' ' + marker_to_register

    def instructions_setup(self,
                           register_instruction_name: str,
                           recording_media: List[Recording]) -> InstructionsSetup:
        return instruction_setup_with_single_phase_with_single_recording_instruction(
            REGISTER_INSTRUCTION_NAME,
            recording_media,
            self.mk_instruction_with_main_action,
            self.mk_instruction_set_for_phase)

    def mk_instruction_set_for_phase(self, instructions: Dict[str, SingleInstructionSetup]) -> InstructionsSetup:
        raise NotImplementedError('abstract method')

    def mk_instruction_with_main_action(self, main_action: Callable) -> Instruction:
        raise NotImplementedError('abstract method')

    def act_phase_parser(self) -> SectionElementParser:
        return ActPhaseParser()


class Files:
    def __init__(self, phase_config: PhaseConfig):
        self.phase_config = phase_config

        self.file_1_with_registering_instruction = File(
            '1.case',
            CASE_THAT_REGISTERS_MARKER.format(
                case_phase_header=self.phase_config.phase_name().syntax,
                phase_contents_line_that_records=self.phase_config.phase_contents_line_that_registers(
                    INSTRUCTION_MARKER_IN_CASE_1))
        )

        self.file_2_with_registering_instruction = File(
            '2.case',
            CASE_THAT_REGISTERS_MARKER.format(
                case_phase_header=self.phase_config.phase_name().syntax,
                phase_contents_line_that_records=self.phase_config.phase_contents_line_that_registers(
                    INSTRUCTION_MARKER_IN_CASE_2))
        )

        self.suite_with_phase_instruction_and_cases = SUITE_WITH_PHASE_INSTRUCTION_AND_CASES.format(
            case_phase_header=self.phase_config.phase_name().syntax,
            phase_contents_line_that_records=self.phase_config.phase_contents_line_that_registers(
                INSTRUCTION_MARKER_IN_CONTAINING_SUITE),
            case_1_file=self.file_1_with_registering_instruction.file_name,
            case_2_file=self.file_2_with_registering_instruction.file_name,
        )

    def suite_with_phase_instruction_but_with_just_a_suite(self, containing_suite_file_name: str) -> str:
        return SUITE_WITH_PHASE_INSTRUCTION_BUT_WITH_JUST_A_SUITE.format(
            case_phase_header=self.phase_config.phase_name().syntax,
            phase_contents_line_that_records=self.phase_config.phase_contents_line_that_registers(
                INSTRUCTION_MARKER_IN_NON_CONTAINING_SUITE),
            sub_suite_file_name=containing_suite_file_name,
        )


class ExpectedRecordingsAssertionConstructor:
    def __init__(self,
                 containing_suite_file_name: str,
                 case_1_file_name: str,
                 case_2_file_name: str,
                 ):
        self.case_2_file_name = case_2_file_name
        self.case_1_file_name = case_1_file_name
        self.containing_suite_file_name = containing_suite_file_name

    def assertion(self, cwd_dir_abs_path: Path) -> ValueAssertion[Sequence[Recording]]:
        raise NotImplementedError('abstract method')

    def _matches_instruction_in_containing_suite(self, cwd_dir_abs_path: Path) -> ValueAssertion[Recording]:
        return self._matches_recording_of(cwd_dir_abs_path,
                                          INSTRUCTION_MARKER_IN_CONTAINING_SUITE,
                                          Path(self.containing_suite_file_name))

    def _matches_instruction_in_case_1(self, cwd_dir_abs_path: Path) -> ValueAssertion[Recording]:
        return self._matches_recording_of(cwd_dir_abs_path,
                                          INSTRUCTION_MARKER_IN_CASE_1,
                                          Path(self.case_1_file_name))

    def _matches_instruction_in_case_2(self, cwd_dir_abs_path: Path) -> ValueAssertion[Recording]:
        return self._matches_recording_of(cwd_dir_abs_path,
                                          INSTRUCTION_MARKER_IN_CASE_2,
                                          Path(self.case_2_file_name))

    @staticmethod
    def _matches_recording_of(cwd_dir_abs_path: Path,
                              string: str,
                              file_path_rel_referrer: Path) -> ValueAssertion[Recording]:
        return matches_recording(
            string=asrt.equals(string),
            file_location_info=matches_file_location_info(
                abs_path_of_dir_containing_first_file_path=asrt.equals(cwd_dir_abs_path),
                file_path_rel_referrer=asrt.equals(file_path_rel_referrer),
                file_inclusion_chain=asrt.is_empty_sequence,
            ),
        )


class ExpectSuiteInstructionsBeforeCaseInstructions(ExpectedRecordingsAssertionConstructor):
    def assertion(self, cwd_dir_abs_path: Path) -> ValueAssertion[Sequence[Recording]]:
        return asrt.matches_sequence([
            # First test case
            self._matches_instruction_in_containing_suite(cwd_dir_abs_path),
            self._matches_instruction_in_case_1(cwd_dir_abs_path),

            # Second test case
            self._matches_instruction_in_containing_suite(cwd_dir_abs_path),
            self._matches_instruction_in_case_2(cwd_dir_abs_path),
        ])


class ExpectCaseInstructionsBeforeSuiteInstructions(ExpectedRecordingsAssertionConstructor):
    def assertion(self, cwd_dir_abs_path: Path) -> ValueAssertion[Sequence[Recording]]:
        return asrt.matches_sequence([
            # First test case
            self._matches_instruction_in_case_1(cwd_dir_abs_path),
            self._matches_instruction_in_containing_suite(cwd_dir_abs_path),

            # Second test case
            self._matches_instruction_in_case_2(cwd_dir_abs_path),
            self._matches_instruction_in_containing_suite(cwd_dir_abs_path),
        ])


class TestBase(unittest.TestCase):
    def _phase_config(self) -> PhaseConfig:
        raise NotImplementedError('abstract method')

    def _expected_instruction_sequencing(self) -> InstructionsSequencing:
        raise NotImplementedError('abstract method')

    def _expected_recordings_assertion(self,
                                       containing_suite_file_name: str,
                                       case_1_file_name: str,
                                       case_2_file_name: str
                                       ) -> ExpectedRecordingsAssertionConstructor:
        if self._expected_instruction_sequencing() is InstructionsSequencing.SUITE_BEFORE_CASE:
            return ExpectSuiteInstructionsBeforeCaseInstructions(containing_suite_file_name,
                                                                 case_1_file_name,
                                                                 case_2_file_name)
        elif self._expected_instruction_sequencing() is InstructionsSequencing.CASE_BEFORE_SUITE:

            return ExpectCaseInstructionsBeforeSuiteInstructions(containing_suite_file_name,
                                                                 case_1_file_name,
                                                                 case_2_file_name)
        else:
            raise ValueError('unknown instruction sequence: ' + str(self._expected_instruction_sequencing()))

    def _phase_instructions_in_suite_containing_cases(self, ):
        # ARRANGE #

        files = Files(self._phase_config())

        containing_suite_file = File('test.suite', files.suite_with_phase_instruction_and_cases)
        suite_and_case_files = DirContents([
            containing_suite_file,
            files.file_1_with_registering_instruction,
            files.file_2_with_registering_instruction,
        ])

        expectation = self._expected_recordings_assertion(
            containing_suite_file.name,
            files.file_1_with_registering_instruction.name,
            files.file_2_with_registering_instruction.name,
        )

        # ACT & ASSERT #
        self._check(containing_suite_file,
                    suite_and_case_files,
                    expectation)

    def _phase_instructions_in_suite_not_containing_cases(self):
        # ARRANGE #

        files = Files(self._phase_config())

        containing_suite_file = File('sub.suite', files.suite_with_phase_instruction_and_cases)
        non_containing_suite_file = File(
            'main.suite',
            files.suite_with_phase_instruction_but_with_just_a_suite(containing_suite_file.file_name)
        )

        suite_and_case_files = DirContents([
            non_containing_suite_file,
            containing_suite_file,
            files.file_1_with_registering_instruction,
            files.file_2_with_registering_instruction,
        ])

        expectation = self._expected_recordings_assertion(
            containing_suite_file.name,
            files.file_1_with_registering_instruction.name,
            files.file_2_with_registering_instruction.name,
        )

        # ACT & ASSERT #
        self._check(containing_suite_file,
                    suite_and_case_files,
                    expectation)

    def _when_syntax_error_in_case_phase_contents_then_suite_parsing_should_raise_exception(self):
        # ARRANGE #
        suite_file = File(
            'the.suite',
            SUITE_WITH_SYNTAX_ERROR_IN_CASE_PHASE.format(case_phase_header=self._phase_config().phase_name().syntax)
        )
        cwd_contents = DirContents([
            suite_file
        ])
        tc_parsing_setup = TestCaseParsingSetup(space_separator_instruction_name_extractor,
                                                InstructionsSetup(),
                                                SectionElementParserThatRaisesUnrecognizedSectionElementSourceError())
        tc_handling_setup = setup_with_null_act_phase_and_null_preprocessing()
        reader = suite_hierarchy_reading.Reader(
            suite_hierarchy_reading.Environment(
                SectionElementParserThatRaisesUnrecognizedSectionElementSourceError(),
                tc_parsing_setup,
                tc_handling_setup)
        )
        with self.assertRaises(SuiteParseError):
            with tmp_dir_as_cwd(cwd_contents):
                # ACT & ASSERT #
                reader.apply(suite_file.name_as_path)

    def _check(self,
               root_suite_file: File,
               suite_and_case_files: DirContents,
               expectation: ExpectedRecordingsAssertionConstructor,
               ):
        case_processors = [
            NameAndValue('processor_that_should_not_pollute_current_process',
                         processors.new_processor_that_should_not_pollute_current_process),
            NameAndValue('processor_that_is_allowed_to_pollute_current_process',
                         processors.new_processor_that_is_allowed_to_pollute_current_process),
        ]
        with tmp_dir_as_cwd(suite_and_case_files) as abs_cwd_dir_path:
            suite_file_path = Path(root_suite_file.name)

            for case_processor_case in case_processors:
                with self.subTest(case_processor_case.name):
                    recording_media = []
                    processor = self._new_processor(recording_media,
                                                    case_processor_case.value)
                    # ACT #

                    return_value = processor.process(suite_file_path, null_output_reporting_environment())

                    # ASSERT #

                    self.assertEqual(ProcessingReporterThatDoesNothing.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')

                    expected_instruction_recording = expectation.assertion(abs_cwd_dir_path)
                    expected_instruction_recording.apply_with_message(self, recording_media, 'recordings'),

    def _new_processor(self,
                       recording_media: List[Recording],
                       test_case_processor_constructor: TestCaseProcessorConstructor) -> sut.Processor:
        test_case_definition = TestCaseDefinition(
            TestCaseParsingSetup(space_separator_instruction_name_extractor,
                                 self._phase_config().instructions_setup(REGISTER_INSTRUCTION_NAME, recording_media),
                                 self._phase_config().act_phase_parser()),
            PredefinedProperties({}, empty_symbol_table()))

        default_case_configuration = processors.Configuration(
            test_case_definition,
            TestCaseHandlingSetup(
                ActPhaseSetup('recording actor', self._phase_config().actor(recording_media)),
                IDENTITY_PREPROCESSOR),
            os_services_access.new_for_current_os(),
            2 ** 10,
            False,
            sandbox_dir_resolving.mk_tmp_dir_with_prefix('test-suite-')
        )

        return sut.Processor(default_case_configuration,
                             suite_hierarchy_reading.Reader(
                                 suite_hierarchy_reading.Environment(
                                     SectionElementParserThatRaisesUnrecognizedSectionElementSourceError(),
                                     test_case_definition.parsing_setup,
                                     default_case_configuration.default_handling_setup)
                             ),
                             ProcessingReporterThatDoesNothing(),
                             enumeration.DepthFirstEnumerator(),
                             test_case_processor_constructor,
                             )
