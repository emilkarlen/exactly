import pathlib
import unittest
from typing import List

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.processing import processors as sut
from exactly_lib.processing.instruction_setup import InstructionsSetup, TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_processing import TestCaseSetup, Status, Result
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation
from exactly_lib_test.execution.test_resources import instruction_test_resources as instr
from exactly_lib_test.processing.test_resources.instruction_set import directive_for_inclusion_of_file
from exactly_lib_test.processing.test_resources.test_case_setup import \
    setup_with_null_act_phase_and_null_preprocessing
from exactly_lib_test.section_document.test_resources.instruction_parser import ParserThatGives
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileInclusion),
    ])


class TestFileInclusion(unittest.TestCase):
    def test_inclusion_of_file_SHOULD_be_possible_in_all_phases_except_act(self):
        name_of_recording_instruction = 'recording-instruction'

        file_to_include = fs.file_with_lines('included-file.src', [
            name_of_recording_instruction,
        ])
        proc_cases = [
            NameAndValue('not allowed to pollute current process',
                         sut.new_processor_that_should_not_pollute_current_process),
            NameAndValue('allowed to pollute current process',
                         sut.new_processor_that_is_allowed_to_pollute_current_process),
        ]
        for phase in phase_identifier.ALL_WITH_INSTRUCTIONS:
            for proc_case in proc_cases:
                with self.subTest(phase.section_name,
                                  proc=proc_case.name):
                    test_case_file = fs.file_with_lines('test.case', [
                        section_header(phase.section_name),
                        directive_for_inclusion_of_file(file_to_include.name),
                    ])
                    cwd_contents = fs.DirContents([test_case_file,
                                                   file_to_include])
                    recording_output = []
                    configuration = configuration_with_instruction_in_each_phase_that_records_phase_name(
                        name_of_recording_instruction,
                        recording_output)
                    processor = proc_case.value(configuration)
                    with tmp_dir_as_cwd(cwd_contents):
                        test_case_setup = TestCaseSetup(pathlib.Path(test_case_file.name),
                                                        file_inclusion_relativity_root=pathlib.Path.cwd())
                        # ACT #
                        result = processor.apply(test_case_setup)
                        # ASSERT #
                        assert isinstance(result, Result)  # Type info for IDE
                        self.assertEqual(Status.EXECUTED,
                                         result.status)
                        self.assertFalse(result.execution_result.is_failure)
                        self.assertEqual(FullResultStatus.PASS,
                                         result.execution_result.status)
                        self.assertEqual([phase.section_name],
                                         recording_output)


def configuration_with_instruction_in_each_phase_that_records_phase_name(
        instruction_name: str,
        recording_output: List[str]) -> sut.Configuration:
    instruction_set = InstructionsSetup(
        config_instruction_set={instruction_name: conf_instr_setup(recording_output)},
        setup_instruction_set={instruction_name: setup_instr_setup(recording_output)},
        before_assert_instruction_set={instruction_name: before_assert_instr_setup(recording_output)},
        assert_instruction_set={instruction_name: assert_instr_setup(recording_output)},
        cleanup_instruction_set={instruction_name: cleanup_instr_setup(recording_output)},
    )
    tc_parsing_setup = TestCaseParsingSetup(
        lambda s: s.split()[0],
        instruction_set,
        ActPhaseParser()
    )
    tc_definition = TestCaseDefinition(tc_parsing_setup,
                                       PredefinedProperties())
    tc_handling_setup = setup_with_null_act_phase_and_null_preprocessing()
    return sut.Configuration(
        tc_definition,
        tc_handling_setup,
        is_keep_sandbox=False,
    )


def conf_instr_setup(recorder: List[str]) -> SingleInstructionSetup:
    return instr_setup(instr.configuration_phase_instruction_that(
        main_initial_action=append_section_name_action(recorder, phase_identifier.CONFIGURATION))
    )


def setup_instr_setup(recorder: List[str]) -> SingleInstructionSetup:
    return instr_setup(instr.setup_phase_instruction_that(
        main_initial_action=append_section_name_action(recorder, phase_identifier.SETUP))
    )


def before_assert_instr_setup(recorder: List[str]) -> SingleInstructionSetup:
    return instr_setup(instr.before_assert_phase_instruction_that(
        main_initial_action=append_section_name_action(recorder, phase_identifier.BEFORE_ASSERT))
    )


def assert_instr_setup(recorder: List[str]) -> SingleInstructionSetup:
    return instr_setup(instr.assert_phase_instruction_that(
        main_initial_action=append_section_name_action(recorder, phase_identifier.ASSERT))
    )


def cleanup_instr_setup(recorder: List[str]) -> SingleInstructionSetup:
    return instr_setup(instr.cleanup_phase_instruction_that(
        main_initial_action=append_section_name_action(recorder, phase_identifier.CLEANUP))
    )


def instr_setup(instruction: Instruction) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser=ParserThatGives(instruction),
        documentation=instruction_documentation('instruction name'),
    )


def append_section_name_action(recorder: List[str], phase: Phase):
    def ret_val(*args, **kwargs):
        recorder.append(phase.section_name)

    return ret_val
