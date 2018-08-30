import unittest
from enum import Enum
from typing import List, Dict, Callable, Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.processing import processors
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.section_document.model import Instruction
from exactly_lib.test_case import os_services
from exactly_lib.test_suite import execution as sut, suite_hierarchy_reading, enumeration
from exactly_lib.test_suite.execution import TestCaseProcessorConstructor
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.section_document.test_resources.element_parsers import \
    SectionElementParserThatRaisesUnrecognizedSectionElementSourceError
from exactly_lib_test.section_document.test_resources.misc import space_separator_instruction_name_extractor
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    test_case_handling_setup_with_identity_preprocessor
from exactly_lib_test.test_suite.test_resources.list_recording_instructions import \
    instruction_setup_with_single_phase_with_single_recording_instruction, Recording, matches_recording
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingRootSuiteReporter, \
    ExecutionTracingReporterFactory

REGISTER_INSTRUCTION_NAME = 'register'
INSTRUCTION_MARKER_IN_CONTAINING_SUITE = 'containing suite'
INSTRUCTION_MARKER_IN_NON_CONTAINING_SUITE = 'non-containing suite'
INSTRUCTION_MARKER_IN_CASE_1 = 'case 1'
INSTRUCTION_MARKER_IN_CASE_2 = 'case 2'
CASE_THAT_REGISTERS_MARKER = """\
{case_phase_header}

register {marker}
"""

SUITE_WITH_PHASE_INSTRUCTION_AND_CASES = """\
[cases]

{case_1_file}
{case_2_file}

{case_phase_header}

register {marker}
"""

SUITE_WITH_PHASE_INSTRUCTION_BUT_WITH_JUST_A_SUITE = """\
[suites]

{sub_suite_file_name}

{case_phase_header}

register {marker}
"""


class InstructionsSequencing(Enum):
    SUITE_BEFORE_CASE = 1
    CASE_BEFORE_SUITE = 2


class Files:
    def __init__(self, case_phase: SectionName):
        self.case_phase = case_phase

        self.file_1_with_registering_instruction = File('1.case',
                                                        CASE_THAT_REGISTERS_MARKER.format(
                                                            case_phase_header=self.case_phase.syntax,
                                                            marker=INSTRUCTION_MARKER_IN_CASE_1))

        self.file_2_with_registering_instruction = File('2.case',
                                                        CASE_THAT_REGISTERS_MARKER.format(
                                                            case_phase_header=self.case_phase.syntax,
                                                            marker=INSTRUCTION_MARKER_IN_CASE_2))

        self.suite_with_phase_instruction_and_cases = SUITE_WITH_PHASE_INSTRUCTION_AND_CASES.format(
            case_phase_header=self.case_phase.syntax,
            marker=INSTRUCTION_MARKER_IN_CONTAINING_SUITE,
            case_1_file=self.file_1_with_registering_instruction.file_name,
            case_2_file=self.file_2_with_registering_instruction.file_name,
        )

    def suite_with_phase_instruction_but_with_just_a_suite(self, containing_suite_file_name: str) -> str:
        return SUITE_WITH_PHASE_INSTRUCTION_BUT_WITH_JUST_A_SUITE.format(
            case_phase_header=self.case_phase.syntax,
            marker=INSTRUCTION_MARKER_IN_NON_CONTAINING_SUITE,
            sub_suite_file_name=containing_suite_file_name,
        )


class PhaseConfig:
    def phase_name(self) -> SectionName:
        raise NotImplementedError('abstract method')

    def mk_instruction_set_for_phase(self, instructions: Dict[str, SingleInstructionSetup]) -> InstructionsSetup:
        raise NotImplementedError('abstract method')

    def mk_instruction_with_main_action(self, main_action: Callable) -> Instruction:
        raise NotImplementedError('abstract method')


class TestBase(unittest.TestCase):
    def _phase_config(self) -> PhaseConfig:
        raise NotImplementedError('abstract method')

    def _expected_instruction_sequencing(self) -> InstructionsSequencing:
        raise NotImplementedError('abstract method')

    def __expected_instruction_recording(self) -> asrt.ValueAssertion[Sequence[Recording]]:
        matches_instruction_in_containing_suite = matches_recording(INSTRUCTION_MARKER_IN_CONTAINING_SUITE)
        matches_instruction_in_case_1 = matches_recording(INSTRUCTION_MARKER_IN_CASE_1)
        matches_instruction_in_case_2 = matches_recording(INSTRUCTION_MARKER_IN_CASE_2)

        if self._expected_instruction_sequencing() is InstructionsSequencing.SUITE_BEFORE_CASE:
            return asrt.matches_sequence([
                # First test case
                matches_instruction_in_containing_suite,
                matches_instruction_in_case_1,

                # Second test case
                matches_instruction_in_containing_suite,
                matches_instruction_in_case_2,
            ])
        elif self._expected_instruction_sequencing() is InstructionsSequencing.CASE_BEFORE_SUITE:
            return asrt.matches_sequence([
                # First test case
                matches_instruction_in_case_1,
                matches_instruction_in_containing_suite,

                # Second test case
                matches_instruction_in_case_2,
                matches_instruction_in_containing_suite,
            ])
        else:
            raise ValueError('implementation error')

    def _phase_instructions_in_suite_containing_cases(self):
        # ARRANGE #

        files = Files(self._phase_config().phase_name())

        containing_suite_file = File('test.suite', files.suite_with_phase_instruction_and_cases)
        suite_and_case_files = DirContents([
            containing_suite_file,
            files.file_1_with_registering_instruction,
            files.file_2_with_registering_instruction,
        ])

        # ACT & ASSERT #
        self._check(containing_suite_file,
                    suite_and_case_files,
                    self.__expected_instruction_recording())

    def _phase_instructions_in_suite_not_containing_cases(self):
        # ARRANGE #

        files = Files(self._phase_config().phase_name())

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

        # ACT & ASSERT #
        self._check(containing_suite_file,
                    suite_and_case_files,
                    self.__expected_instruction_recording())

    def _check(self,
               containing_suite_file: File,
               suite_and_case_files: DirContents,
               expected_instruction_recording: asrt.ValueAssertion[List[Recording]],
               ):
        case_processors = [
            NameAndValue('processor_that_should_not_pollute_current_process',
                         processors.new_processor_that_should_not_pollute_current_process),
            NameAndValue('processor_that_is_allowed_to_pollute_current_process',
                         processors.new_processor_that_is_allowed_to_pollute_current_process),
        ]
        with tmp_dir(suite_and_case_files) as tmp_dir_path:
            suite_file_path = tmp_dir_path / containing_suite_file.file_name

            for case_processor_case in case_processors:
                with self.subTest(case_processor_case.name):
                    recording_media = []
                    executor = self._new_executor(recording_media,
                                                  case_processor_case.value)
                    # ACT #

                    return_value = executor.execute(suite_file_path, StringStdOutFiles().stdout_files)

                    # ASSERT #

                    self.assertEqual(ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')
                    expected_instruction_recording.apply_with_message(self, recording_media, 'recordings'),

    def _new_executor(self,
                      recorder: List[Recording],
                      test_case_processor_constructor: TestCaseProcessorConstructor) -> sut.Executor:
        instructions_setup = instruction_setup_with_single_phase_with_single_recording_instruction(
            REGISTER_INSTRUCTION_NAME,
            recorder,
            self._phase_config().mk_instruction_with_main_action,
            self._phase_config().mk_instruction_set_for_phase)

        test_case_definition = TestCaseDefinition(
            TestCaseParsingSetup(space_separator_instruction_name_extractor,
                                 instructions_setup,
                                 ActPhaseParser()),
            PredefinedProperties({}, empty_symbol_table()))

        default_configuration = processors.Configuration(test_case_definition,
                                                         test_case_handling_setup_with_identity_preprocessor(),
                                                         os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                                                         False,
                                                         sandbox_dir_resolving.mk_tmp_dir_with_prefix('test-suite-'))

        return sut.Executor(default_configuration,
                            suite_hierarchy_reading.Reader(
                                suite_hierarchy_reading.Environment(
                                    SectionElementParserThatRaisesUnrecognizedSectionElementSourceError(),
                                    test_case_definition.parsing_setup,
                                    default_configuration.default_handling_setup)
                            ),
                            ExecutionTracingReporterFactory(),
                            enumeration.DepthFirstEnumerator(),
                            test_case_processor_constructor,
                            )
