import pathlib
import unittest

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, TestSuiteDefinition
from exactly_lib.common import instruction_setup
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.help_texts.test_case.phase_names import ASSERT_PHASE_NAME, ACT_PHASE_NAME
from exactly_lib.help_texts.test_suite.section_names_with_syntax import SECTION_NAME__CONF
from exactly_lib.processing import exit_values
from exactly_lib.processing import instruction_setup
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.std import StdFiles
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.test_case.config_from_suite.test_resources import cli_args_for, run_test_case, \
    test_suite_definition_without_instructions, test_suite_definition_with_instructions
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.execution.test_resources.act_source_executor import ActSourceAndExecutorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorConstructorForConstantExecutor
from exactly_lib_test.execution.test_resources.instruction_test_resources import assert_phase_instruction_that
from exactly_lib_test.processing.processing_utils import PreprocessorThat
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions.process_result_assertions import is_result_for_exit_value


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestConfigFromSuiteShouldBeForwardedToTestCase(),
        TestSyntaxErrorInSuiteFile(),
    ])


SUCCESS_INDICATOR_STRING = 'output from actor set in suite'


class TestConfigFromSuiteShouldBeForwardedToTestCase(unittest.TestCase):
    def runTest(self):
        default_test_case_handling = TestCaseHandlingSetup(
            act_phase_setup=act_setup_that_does_nothing(),
            preprocessor=IdentityPreprocessor()
        )

        test_suite_definition = test_suite_definition_with_single_conf_instruction(
            name=SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME,
            instruction=
            SuiteConfInstructionThatSets(
                preprocessor=preprocessor_that_gives_const_source_with_single_assert_instruction(
                    ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_IS_SUCCESS_INDICATOR_STRING__NAME
                ),
                act_phase_setup=act_setup_that_prints_single_string_on_stdout(
                    SUCCESS_INDICATOR_STRING
                )
            )
        )

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

        suite_file_name = 'test.suite'
        case_file_name = 'test.case'

        command_line_arguments = cli_args_for(
            suite_file=suite_file_name,
            case_file=case_file_name,
        )

        suite_and_case_files = DirContents([
            File(suite_file_name,
                 test_suite_source_with_single_conf_instruction(
                     SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME
                 )),
            File(case_file_name,
                 test_case_source_with_single_assert_phase_instruction(
                     ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY__NAME)),
        ])

        # ACT #
        actual_result = run_test_case(command_line_arguments,
                                      suite_and_case_files,
                                      test_case_definition,
                                      test_suite_definition,
                                      default_test_case_handling)
        # ASSERT #
        if actual_result.exitcode != exit_values.EXECUTION__PASS.exit_code:
            self.fail(_error_message(actual_result))


class TestSyntaxErrorInSuiteFile(unittest.TestCase):
    def runTest(self):
        default_test_case_handling = TestCaseHandlingSetup(
            act_phase_setup=act_setup_that_does_nothing(),
            preprocessor=IdentityPreprocessor()
        )

        test_suite_definition = test_suite_definition_without_instructions()

        test_case_definition = test_case_definition_with_only_assert_phase_instructions([])

        suite_file_name = 'test.suite'
        case_file_name = 'test.case'

        command_line_arguments = cli_args_for(
            suite_file=suite_file_name,
            case_file=case_file_name,
        )

        suite_and_case_files = DirContents([
            File(suite_file_name,
                 '[this_is_not_a_suite_section]\n'),
            File(case_file_name,
                 test_case_source_with_single_act_phase_instruction('act-phase-content-that-should-be-ignored')),
        ])

        # ACT #
        actual_result = run_test_case(command_line_arguments,
                                      suite_and_case_files,
                                      test_case_definition,
                                      test_suite_definition,
                                      default_test_case_handling)
        # ASSERT #
        expectation = is_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR)
        expectation.apply_without_message(self, actual_result)


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
        SECTION_NAME__CONF.syntax,
        instruction,
    ])


def test_case_source_with_single_assert_phase_instruction(instruction: str) -> str:
    return lines_content([
        ASSERT_PHASE_NAME.syntax,
        instruction,
    ])


def test_case_source_with_single_act_phase_instruction(instruction: str) -> str:
    return lines_content([
        ACT_PHASE_NAME.syntax,
        instruction,
    ])


SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR__NAME = \
    'SUITE_CONF_INSTRUCTION_THAT_SETS_PREPROCESSOR_AND_ACTOR'

ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_IS_SUCCESS_INDICATOR_STRING__NAME = \
    'ASSERT_PHASE_INSTRUCTION_THAT_PASS_IFF_STDOUT_EQUALS'

ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY__NAME = 'ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY'


def test_suite_definition_with_single_conf_instruction(name: str,
                                                       instruction: ConfigurationSectionInstruction) -> TestSuiteDefinition:
    configuration_section_instructions = {
        name: single_instruction_setup(name, instruction)

    }
    return test_suite_definition_with_instructions(configuration_section_instructions)


def test_case_definition_with_only_assert_phase_instructions(assert_phase_instructions: list
                                                             ) -> TestCaseDefinitionForMainProgram:
    def mk_setup(name_and_instruction):
        return name_and_instruction[0], single_instruction_setup(name_and_instruction[0], name_and_instruction[1])

    assert_phase_instructions_dict = dict(map(mk_setup, assert_phase_instructions))
    return TestCaseDefinitionForMainProgram(
        instruction_name_extractor_function=instruction_name_and_argument_splitter.splitter,
        instruction_setup=instruction_setup.InstructionsSetup(
            config_instruction_set={},
            setup_instruction_set={},
            assert_instruction_set=assert_phase_instructions_dict,
            before_assert_instruction_set={},
            cleanup_instruction_set={},
        ),
        builtin_symbols=[]
    )


ASSERT_PHASE_INSTRUCTION_THAT_FAILS_UNCONDITIONALLY = assert_phase_instruction_that(
    main=do_return(pfh.new_pfh_fail('unconditional failure')))


def assert_phase_instruction_that_pass_iff_stdout_is_success_indicator_string(expected: str) -> AssertPhaseInstruction:
    return AssertPhaseInstructionThatPassIffStdoutEqualsString(expected)


class AssertPhaseInstructionThatPassIffStdoutEqualsString(AssertPhaseInstruction):
    def __init__(self, expected: str):
        self.expected = expected

    def main(self, environment: InstructionEnvironmentForPostSdsStep,
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


def act_setup_that_prints_single_string_on_stdout(string_to_print: str) -> ActPhaseSetup:
    return ActPhaseSetup(ActSourceAndExecutorConstructorForConstantExecutor(
        ActSourceAndExecutorThatRunsConstantActions(
            execute_initial_action=PrintStringOnStdout(string_to_print)))
    )


def act_setup_that_does_nothing() -> ActPhaseSetup:
    return ActPhaseSetup(ActSourceAndExecutorConstructorForConstantExecutor(
        ActSourceAndExecutorThatRunsConstantActions())
    )


class PrintStringOnStdout:
    def __init__(self, string_to_print: str):
        self.string_to_print = string_to_print

    def __call__(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 script_output_dir_path: pathlib.Path,
                 std_files: StdFiles):
        std_files.output.out.write(self.string_to_print)
