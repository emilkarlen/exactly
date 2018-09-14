import unittest
from pathlib import Path
from typing import Optional

from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.definitions.test_suite.section_names import CONFIGURATION
from exactly_lib.processing import exit_values
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.standalone import processor as sut
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import pfh
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.string import lines_content
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.execution.test_resources.instruction_test_resources import assert_phase_instruction_that
from exactly_lib_test.processing.processing_utils import PreprocessorThat
from exactly_lib_test.processing.standalone.test_resources.run_processor import capture_output_from_processor
from exactly_lib_test.processing.test_resources.act_phase import act_setup_that_prints_single_string_on_stdout
from exactly_lib_test.processing.test_resources.test_case_setup import \
    test_case_definition_with_only_assert_phase_instructions, setup_with_null_act_phase_and_null_preprocessing
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatJustReturnsConstant
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_suite.test_resources.test_suite_definition import configuration_section_parser
from exactly_lib_test.test_suite.test_resources.test_suite_definition import test_suite_definition_with_instructions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConfigFromSuiteShouldBeForwardedToTestCase),
    ])


SUCCESS_INDICATOR_STRING = 'output from actor set in suite'


class TestConfigFromSuiteShouldBeForwardedToTestCase(unittest.TestCase):
    def test_explicit_suite_file(self):
        suite_file_name = Path('test.suite')

        self._run(suite_file_name=str(suite_file_name),
                  suite_file_overriding=suite_file_name)

    def test_implicit_default_suite(self):
        self._run(suite_file_name=file_names.DEFAULT_SUITE_FILE,
                  suite_file_overriding=None)

    def _run(self,
             suite_file_name: str,
             suite_file_overriding: Optional[Path]):
        default_test_case_handling = setup_with_null_act_phase_and_null_preprocessing()

        suite_conf_instruction = SuiteConfInstructionThatSets(
            preprocessor=preprocessor_that_gives_const_source_with_single_assert_instruction(
                ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_IS_SUCCESS_INDICATOR_STRING__NAME),
            act_phase_setup=act_setup_that_prints_single_string_on_stdout(SUCCESS_INDICATOR_STRING))

        suite_conf_instructions = {
            SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME:
                single_instruction_setup(SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME,
                                         suite_conf_instruction)

        }

        suite_conf_parser = configuration_section_parser(suite_conf_instructions)

        test_case_definition = test_case_definition_with_only_assert_phase_instructions([
            (
                ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_IS_SUCCESS_INDICATOR_STRING__NAME,
                assert_phase_instruction_that_pass_iff_stdout_is_success_indicator_string(SUCCESS_INDICATOR_STRING)
            ),
            (
                ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY__NAME,
                ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY,
            ),
        ])
        processor = sut.Processor(test_case_definition,
                                  ActPhaseOsProcessExecutorThatJustReturnsConstant(),
                                  suite_conf_parser)

        suite_file = File(
            suite_file_name,
            test_suite_source_with_single_conf_instruction(
                SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME)
        )
        case_file = File(
            'test.case',
            test_case_source_with_single_assert_phase_instruction(
                ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY__NAME)
        )

        sub_dir_path = Path('sub-dir')

        suite_and_case_files = DirContents([
            suite_file,
            case_file,
        ]).in_dir(str(sub_dir_path))

        explicit_suite_file_path = None
        if suite_file_overriding:
            explicit_suite_file_path = sub_dir_path / suite_file_overriding

        with tmp_dir_as_cwd(suite_and_case_files) as tmp_dir:
            execution_settings = TestCaseExecutionSettings(sub_dir_path / case_file.name_as_path,
                                                           tmp_dir / sub_dir_path,
                                                           ReportingOption.STATUS_CODE,
                                                           default_test_case_handling,
                                                           suite_to_read_config_from=explicit_suite_file_path)

            # ACT #
            actual_result = capture_output_from_processor(processor,
                                                          execution_settings)
        # ASSERT #
        if actual_result.exitcode != exit_values.EXECUTION__PASS.exit_code:
            self.fail(_error_message(actual_result))


def _error_message(actual: SubProcessResult) -> str:
    s = ('\n'
         'Unexpected exit code: {unexpected}\n'
         'Expected            : {expected}\n'
         'stdout="{stdout}"\n'
         'stderr="{stderr}"\n')
    err_msg = s.format(
        unexpected=str(actual.exitcode),
        expected=str(exit_values.EXECUTION__PASS.exit_code),
        stdout=actual.stdout,
        stderr=actual.stderr)
    return err_msg


def preprocessor_that_gives_const_source_with_single_assert_instruction(instruction: str) -> Preprocessor:
    return preprocessor_that_gives_constant(
        test_case_source_with_single_assert_phase_instruction(
            instruction
        ),
    )


def test_suite_source_with_single_conf_instruction(instruction: str) -> str:
    return lines_content([
        CONFIGURATION.syntax,
        instruction,
    ])


def test_case_source_with_single_assert_phase_instruction(instruction: str) -> str:
    return lines_content([
        phase_names.ASSERT.syntax,
        instruction,
    ])


SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME = \
    'SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR'

ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_IS_SUCCESS_INDICATOR_STRING__NAME = \
    'ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_EQUALS'

ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY__NAME = 'ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY'


def test_suite_definition_with_single_conf_instruction(name: str,
                                                       instruction: ConfigurationSectionInstruction
                                                       ) -> TestSuiteDefinition:
    configuration_section_instructions = {
        name: single_instruction_setup(name, instruction)

    }
    return test_suite_definition_with_instructions(configuration_section_instructions)


ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY = assert_phase_instruction_that(
    main=do_return(pfh.new_pfh_fail('unconditional failure')))


def assert_phase_instruction_that_pass_iff_stdout_is_success_indicator_string(expected: str) -> AssertPhaseInstruction:
    return AssertPhaseInstructionThatPassIffStdoutEqualsString(expected)


class AssertPhaseInstructionThatPassIffStdoutEqualsString(AssertPhaseInstruction):
    def __init__(self, expected: str):
        self.expected = expected

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_contents = environment.sds.result.stdout_file.read_text()
        if actual_contents == self.expected:
            return pfh.new_pfh_pass()
        else:
            err_msg = 'Expected: {}\nActual  : {}'.format(self.expected, actual_contents)
            return pfh.new_pfh_fail(err_msg)


def preprocessor_that_gives_constant(s: str) -> Preprocessor:
    return PreprocessorThat(do_return(s))


class SuiteConfInstructionThatSets(ConfigurationSectionInstruction):
    def __init__(self,
                 preprocessor: Preprocessor,
                 act_phase_setup: ActPhaseSetup
                 ):
        self.preprocessor = preprocessor
        self.act_phase_setup = act_phase_setup

    def execute(self, environment: ConfigurationSectionEnvironment):
        environment.preprocessor = self.preprocessor
        environment.act_phase_setup = self.act_phase_setup
