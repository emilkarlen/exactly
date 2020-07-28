import pathlib
import unittest
from typing import List, Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.processing import processors as sut
from exactly_lib.processing.instruction_setup import InstructionsSetup, TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_processing import Status, Result, Processor, AccessErrorType, \
    test_case_reference_of_source_file
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.source_location import SourceLocationPath, source_location_path_of, SourceLocation
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import atc_os_proc_executors, os_services_access
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.util.line_source import Line, single_line_sequence
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation
from exactly_lib_test.execution.test_resources import instruction_test_resources as instr
from exactly_lib_test.processing.test_resources.instruction_set import directive_for_inclusion_of_file
from exactly_lib_test.processing.test_resources.result_assertions import result_is_access_error, \
    result_for_executed_status_matches
from exactly_lib_test.processing.test_resources.test_case_setup import \
    setup_with_null_act_phase_and_null_preprocessing, configuration_with_no_instructions_and_no_preprocessor
from exactly_lib_test.section_document.test_resources.instruction_parser import ParserThatGives
from exactly_lib_test.section_document.test_resources.source_location_assertions import equals_source_location_path
from exactly_lib_test.test_resources.actions import do_return, do_raise
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileInclusionResultStatus),
        unittest.makeSuite(TestFileInclusionSourceLocationPathsWithMultipleInclusions),
    ])


class TestFileInclusionResultStatus(unittest.TestCase):
    def test_inclusion_of_file_SHOULD_be_possible_in_all_phases_except_act(self):
        # ARRANGE #
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
                        test_case_reference = test_case_reference_of_source_file(pathlib.Path(test_case_file.name))
                        # ACT #
                        result = processor.apply(test_case_reference)
                        # ASSERT #
                        assert isinstance(result, Result)  # Type info for IDE
                        self.assertEqual(Status.EXECUTED,
                                         result.status)
                        self.assertFalse(result.execution_result.is_failure)
                        self.assertEqual(FullExeResultStatus.PASS,
                                         result.execution_result.status)
                        self.assertEqual([phase.section_name],
                                         recording_output)

    def test_inclusion_of_non_exiting_file_SHOULD_cause_file_access_error(self):
        # ARRANGE #
        name_of_non_existing_file = 'non-existing.src'
        configuration = configuration_with_no_instructions_and_no_preprocessor()
        proc_cases = [
            NameAndValue('not allowed to pollute current process',
                         sut.new_processor_that_should_not_pollute_current_process(configuration)),
            NameAndValue('allowed to pollute current process',
                         sut.new_processor_that_is_allowed_to_pollute_current_process(configuration)),
        ]
        for phase in phase_identifier.ALL_WITH_INSTRUCTIONS:
            for proc_case in proc_cases:
                with self.subTest(phase.section_name,
                                  proc=proc_case.name):
                    test_case_file = fs.file_with_lines('test.case', [
                        section_header(phase.section_name),
                        directive_for_inclusion_of_file(name_of_non_existing_file),
                    ])
                    cwd_contents = fs.DirContents([test_case_file])
                    processor = proc_case.value
                    assert isinstance(processor, Processor)
                    with tmp_dir_as_cwd(cwd_contents):
                        test_case_reference = test_case_reference_of_source_file(pathlib.Path(test_case_file.name))
                        # ACT #
                        result = processor.apply(test_case_reference)
                        # ASSERT #
                        assert isinstance(result, Result)  # Type info for IDE
                        self.assertEqual(Status.ACCESS_ERROR,
                                         result.status)
                        self.assertEqual(AccessErrorType.FILE_ACCESS_ERROR,
                                         result.access_error_type)
                        source_location_path_expectation = equals_source_location_path(
                            source_location_path_of(pathlib.Path(test_case_file.name),
                                                    Line(2,
                                                         directive_for_inclusion_of_file(name_of_non_existing_file))))
                        source_location_path_expectation.apply_with_message(self,
                                                                            result.error_info.source_location_path,
                                                                            'source location path')


class SourceAndStatus:
    def __init__(self,
                 failing_source_line: str,
                 expected_result_statuses: ValueAssertion[Result]
                 ):
        self.failing_source_line = failing_source_line
        self.expected_result_statuses = expected_result_statuses


class TestFileInclusionSourceLocationPathsWithMultipleInclusions(unittest.TestCase):
    def _check_failing_line(self,
                            configuration: sut.Configuration,
                            phases: Sequence[Phase],
                            invalid_line_cases: Sequence[NameAndValue[SourceAndStatus]]):
        proc_cases = [
            NameAndValue('not allowed to pollute current process',
                         sut.new_processor_that_should_not_pollute_current_process(configuration)),
            NameAndValue('allowed to pollute current process',
                         sut.new_processor_that_is_allowed_to_pollute_current_process(configuration)),
        ]
        for phase in phases:
            for invalid_line_case in invalid_line_cases:
                source_and_status = invalid_line_case.value
                assert isinstance(source_and_status, SourceAndStatus)  # Type info for IDE

                file_with_error = fs.file_with_lines('file-with-error.src', [
                    source_and_status.failing_source_line,
                ])
                erroneous_line = single_line_sequence(1, source_and_status.failing_source_line)

                test_case_file = fs.file_with_lines('test.case', [
                    section_header(phase.section_name),
                    directive_for_inclusion_of_file(file_with_error.name),
                ])
                line_that_includes_erroneous_file = single_line_sequence(2, directive_for_inclusion_of_file(
                    file_with_error.name))

                cwd_contents = fs.DirContents([test_case_file,
                                               file_with_error])

                expected_source_location_path = SourceLocationPath(
                    location=SourceLocation(erroneous_line,
                                            pathlib.Path(file_with_error.name)),
                    file_inclusion_chain=[SourceLocation(line_that_includes_erroneous_file,
                                                         pathlib.Path(test_case_file.name))])

                for proc_case in proc_cases:
                    with self.subTest(phase=phase.section_name,
                                      proc=proc_case.name,
                                      line=erroneous_line.first_line):
                        processor = proc_case.value
                        assert isinstance(processor, Processor)
                        with tmp_dir_as_cwd(cwd_contents):
                            test_case_reference = test_case_reference_of_source_file(pathlib.Path(test_case_file.name))
                            # ACT #
                            result = processor.apply(test_case_reference)
                            # ASSERT #
                            assert isinstance(result, Result)  # Type info for IDE

                            source_and_status.expected_result_statuses.apply_with_message(self,
                                                                                          result,
                                                                                          'result statuses')

                            source_location_path_expectation = equals_source_location_path(
                                expected_source_location_path)
                            source_location_path_expectation.apply_with_message(self,
                                                                                result.source_location_path,
                                                                                'source location path')

    def test_test_case_not_executed(self):
        self._check_failing_line(
            configuration=configuration_with_no_instructions_and_no_preprocessor(),
            phases=phase_identifier.ALL_WITH_INSTRUCTIONS,
            invalid_line_cases=[
                NameAndValue('inclusion of non-existing file',
                             SourceAndStatus(
                                 failing_source_line=directive_for_inclusion_of_file('non-existing.src'),
                                 expected_result_statuses=result_is_access_error(AccessErrorType.FILE_ACCESS_ERROR))),
                NameAndValue('non-existing instruction',
                             SourceAndStatus(
                                 failing_source_line='non-existing-instruction',
                                 expected_result_statuses=result_is_access_error(AccessErrorType.SYNTAX_ERROR))),
            ])

    def test_instruction_with_implementation_error(self):
        name_of_failing_instruction = 'instruction-with-implementation-error'
        self._check_failing_line(
            configuration=configuration_with_instruction_in_each_phase_with_implementation_error(
                name_of_failing_instruction),
            phases=phase_identifier.ALL_WITH_INSTRUCTIONS,
            invalid_line_cases=[
                NameAndValue('implementation error',
                             SourceAndStatus(
                                 failing_source_line=name_of_failing_instruction,
                                 expected_result_statuses=result_for_executed_status_matches(
                                     FullExeResultStatus.IMPLEMENTATION_ERROR))),
            ])

    def test_instruction_validation_fails(self):
        name_of_failing_instruction = 'validation-failing-instruction'
        self._check_failing_line(
            configuration=configuration_with_instruction_in_each_phase_with_failing_validation(
                name_of_failing_instruction),
            phases=(phase_identifier.SETUP,
                    phase_identifier.BEFORE_ASSERT,
                    phase_identifier.ASSERT,
                    phase_identifier.CLEANUP),
            invalid_line_cases=[
                NameAndValue('failing validation',
                             SourceAndStatus(
                                 failing_source_line=name_of_failing_instruction,
                                 expected_result_statuses=result_for_executed_status_matches(
                                     FullExeResultStatus.VALIDATION_ERROR))),
            ])

    def test_assertion_fails(self):
        name_of_failing_instruction = 'failing-assertion-instruction'
        self._check_failing_line(
            configuration=configuration_with_assert_instruction_that_fails(name_of_failing_instruction),
            phases=[phase_identifier.ASSERT],
            invalid_line_cases=[
                NameAndValue('failing assertion',
                             SourceAndStatus(
                                 failing_source_line=name_of_failing_instruction,
                                 expected_result_statuses=result_for_executed_status_matches(
                                     FullExeResultStatus.FAIL))),
            ])


def configuration_with_assert_instruction_that_fails(instruction_name: str) -> sut.Configuration:
    assert_instruction_setup = instr_setup(instr.assert_phase_instruction_that(
        main=do_return(pfh.new_pfh_fail__str('fail error message')))
    )

    instruction_set = InstructionsSetup(
        config_instruction_set={},
        setup_instruction_set={},
        before_assert_instruction_set={},
        assert_instruction_set={instruction_name: assert_instruction_setup},
        cleanup_instruction_set={},
    )
    return configuration_for_instruction_set(instruction_set)


def configuration_with_instruction_in_each_phase_with_failing_validation(
        instruction_name: str) -> sut.Configuration:
    instr_setup_factory = InstructionWithFailingValidationFactory()
    instruction_set = InstructionsSetup(
        config_instruction_set={instruction_name: instr_setup_factory.conf_instr_setup()},
        setup_instruction_set={instruction_name: instr_setup_factory.setup_instr_setup()},
        before_assert_instruction_set={instruction_name: instr_setup_factory.before_assert_instr_setup()},
        assert_instruction_set={instruction_name: instr_setup_factory.assert_instr_setup()},
        cleanup_instruction_set={instruction_name: instr_setup_factory.cleanup_instr_setup()},
    )
    return configuration_for_instruction_set(instruction_set)


def configuration_with_instruction_in_each_phase_with_implementation_error(
        instruction_name: str) -> sut.Configuration:
    instr_setup_factory = InstructionWithImplementationErrorFactory()
    instruction_set = InstructionsSetup(
        config_instruction_set={instruction_name: instr_setup_factory.conf_instr_setup()},
        setup_instruction_set={instruction_name: instr_setup_factory.setup_instr_setup()},
        before_assert_instruction_set={instruction_name: instr_setup_factory.before_assert_instr_setup()},
        assert_instruction_set={instruction_name: instr_setup_factory.assert_instr_setup()},
        cleanup_instruction_set={instruction_name: instr_setup_factory.cleanup_instr_setup()},
    )
    return configuration_for_instruction_set(instruction_set)


def configuration_with_instruction_in_each_phase_that_records_phase_name(
        instruction_name: str,
        recording_output: List[str]) -> sut.Configuration:
    instr_setup_factory = PhaseRecordingInstructionFactory(recording_output)
    instruction_set = InstructionsSetup(
        config_instruction_set={instruction_name: instr_setup_factory.conf_instr_setup()},
        setup_instruction_set={instruction_name: instr_setup_factory.setup_instr_setup()},
        before_assert_instruction_set={instruction_name: instr_setup_factory.before_assert_instr_setup()},
        assert_instruction_set={instruction_name: instr_setup_factory.assert_instr_setup()},
        cleanup_instruction_set={instruction_name: instr_setup_factory.cleanup_instr_setup()},
    )
    return configuration_for_instruction_set(instruction_set)


def configuration_for_instruction_set(instruction_set: InstructionsSetup) -> sut.Configuration:
    tc_parsing_setup = TestCaseParsingSetup(
        first_space_separated_string_extractor,
        instruction_set,
        ActPhaseParser()
    )
    tc_definition = TestCaseDefinition(tc_parsing_setup,
                                       PredefinedProperties({}))
    tc_handling_setup = setup_with_null_act_phase_and_null_preprocessing()
    return sut.Configuration(
        tc_definition,
        tc_handling_setup,
        atc_os_proc_executors.DEFAULT_ATC_OS_PROCESS_EXECUTOR,
        os_services_access.new_for_current_os(),
        is_keep_sandbox=False,
    )


def first_space_separated_string_extractor(s: str) -> str:
    return s.split()[0]


class PhaseRecordingInstructionFactory:
    """
    Builds instructions that records the name of the phase, by appending it to a list.
    """

    def __init__(self, recording_output: List[str]):
        self.recording_output = recording_output

    def conf_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.configuration_phase_instruction_that(
            main_initial_action=append_section_name_action(self.recording_output, phase_identifier.CONFIGURATION))
        )

    def setup_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.setup_phase_instruction_that(
            main_initial_action=append_section_name_action(self.recording_output, phase_identifier.SETUP))
        )

    def before_assert_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.before_assert_phase_instruction_that(
            main_initial_action=append_section_name_action(self.recording_output, phase_identifier.BEFORE_ASSERT))
        )

    def assert_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.assert_phase_instruction_that(
            main_initial_action=append_section_name_action(self.recording_output, phase_identifier.ASSERT))
        )

    def cleanup_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.cleanup_phase_instruction_that(
            main_initial_action=append_section_name_action(self.recording_output, phase_identifier.CLEANUP))
        )


class InstructionWithFailingValidationFactory:
    """
    Builds instructions that causes validation error (except for conf phase).
    """

    def __init__(self):
        self.do_return_validation_error = do_return(svh.new_svh_validation_error__str('validation error message'))

    def conf_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.configuration_phase_instruction_that())

    def setup_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.setup_phase_instruction_that(
            validate_pre_sds=self.do_return_validation_error
        ))

    def before_assert_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.before_assert_phase_instruction_that(
            validate_pre_sds=self.do_return_validation_error)
        )

    def assert_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.assert_phase_instruction_that(
            validate_pre_sds=self.do_return_validation_error)
        )

    def cleanup_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.cleanup_phase_instruction_that(
            validate_pre_sds=self.do_return_validation_error)
        )


class InstructionWithImplementationErrorFactory:
    """
    Builds instructions that raises an exception that indicates implementation error.
    """

    def conf_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.configuration_phase_instruction_that(
            main_initial_action=do_raise(ImplementationError())
        ))

    def setup_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.setup_phase_instruction_that(
            main_initial_action=do_raise(ImplementationError())
        ))

    def before_assert_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.before_assert_phase_instruction_that(
            main_initial_action=do_raise(ImplementationError())
        ))

    def assert_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.assert_phase_instruction_that(
            main_initial_action=do_raise(ImplementationError())
        ))

    def cleanup_instr_setup(self) -> SingleInstructionSetup:
        return instr_setup(instr.cleanup_phase_instruction_that(
            main_initial_action=do_raise(ImplementationError())
        ))


def instr_setup(instruction: Instruction) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser=ParserThatGives(instruction),
        documentation=instruction_documentation('instruction name'),
    )


def append_section_name_action(recorder: List[str], phase: Phase):
    def ret_val(*args, **kwargs):
        recorder.append(phase.section_name)

    return ret_val


class ImplementationError(Exception):
    pass
