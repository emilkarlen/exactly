import unittest

import pathlib
import tempfile
from typing import Any, Callable, Dict

from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import \
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution.phase_step import STEP__MAIN, STEP__VALIDATE_POST_SETUP, \
    STEP__ACT__PREPARE, STEP__ACT__EXECUTE, STEP__ACT__PARSE, STEP__VALIDATE_PRE_SDS
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.exit_values import EXECUTION__IMPLEMENTATION_ERROR, EXECUTION__HARD_ERROR, EXECUTION__FAIL, \
    EXECUTION__VALIDATION_ERROR, EXECUTION__PASS, NO_EXECUTION__SYNTAX_ERROR
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ActionToCheckExecutorParser
from exactly_lib.test_case.phase_identifier import Phase, PhaseEnum
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.result import pfh, sh, svh
from exactly_lib.util.file_utils import resolved_path_name
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import main_program_of, \
    capture_output_from_main_program__in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    assert_phase_instruction_that, before_assert_phase_instruction_that, cleanup_phase_instruction_that
from exactly_lib_test.processing.test_resources.instruction_set import instruction_set
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActionToCheckExecutorParserThatRunsConstantActions
from exactly_lib_test.test_resources.actions import do_return, do_raise
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import T, MessageBuilder, ValueAssertion, \
    ValueAssertionBase
from exactly_lib_test.test_suite.test_resources.test_suite_definition import test_suite_definition_without_instructions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailureBeforeCreationOfSds),
        unittest.makeSuite(TestPhasesInPartialExecution),
    ])


class Arrangement:
    def __init__(self,
                 phase: Phase,
                 instruction: TestCaseInstruction
                 ):
        self.phase = phase
        self.instruction = instruction

    def instruction_setup_with_the_instruction(self, instruction_name: str) -> InstructionsSetup:
        instruction_setup = single_instruction_setup(instruction_name, self.instruction)
        config = dict()
        setup = dict()
        before_assert = dict()
        assert_ = dict()
        cleanup = dict()

        phase_enum = self.phase.the_enum
        if phase_enum is PhaseEnum.SETUP:
            setup[instruction_name] = instruction_setup
        elif phase_enum is PhaseEnum.BEFORE_ASSERT:
            before_assert[instruction_name] = instruction_setup
        elif phase_enum is PhaseEnum.ASSERT:
            assert_[instruction_name] = instruction_setup
        elif phase_enum is PhaseEnum.CLEANUP:
            cleanup[instruction_name] = instruction_setup
        else:
            raise ValueError('Unhandled phase: ' + str(phase_enum))

        return InstructionsSetup(config_instruction_set=config,
                                 setup_instruction_set=setup,
                                 before_assert_instruction_set=before_assert,
                                 assert_instruction_set=assert_,
                                 cleanup_instruction_set=cleanup
                                 )


class Expectation:
    def __init__(self,
                 exit_vale: ExitValue,
                 output_assertion_for_sds_dir_name: Callable[[str], ValueAssertion[str]]
                 ):
        self.exit_vale = exit_vale
        self.output_assertion_for_sds_dir_name = output_assertion_for_sds_dir_name


class Case:
    def __init__(self,
                 arrangement: Arrangement,
                 expectation: Expectation
                 ):
        self.arrangement = arrangement
        self.expectation = expectation


class TestFailureBeforeCreationOfSds(unittest.TestCase):
    def test_failing_parse(self):
        # ARRANGE #
        test_case_definition = test_case_definition_for(instruction_set())
        atc_e_parser = ActionToCheckExecutorParserThatRunsConstantActions()
        test_case_source = lines_content([
            section_header(phase_identifier.SETUP.identifier),
            'not_the_name_of_an_instruction',
        ])

        expectation = Expectation(NO_EXECUTION__SYNTAX_ERROR, output_is_empty)
        # ACT & ASSERT #
        _check(self,
               test_case_definition,
               atc_e_parser,
               test_case_source,
               self.sandbox_dir_resolver_that_should_not_be_called,
               expectation)

    def test_setup(self):
        # ARRANGE #
        cases = {
            EXECUTION__VALIDATION_ERROR:
                setup_phase_instruction_that(validate_pre_sds=SVH_VALIDATION_ERROR),

            EXECUTION__HARD_ERROR:
                setup_phase_instruction_that(validate_pre_sds=SVH_HARD_ERROR),

            EXECUTION__IMPLEMENTATION_ERROR:
                setup_phase_instruction_that(validate_pre_sds_initial_action=DO_RAISES_EXCEPTION),
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_not_created_and_stdout_is_empty(phase_identifier.SETUP, cases)

    def test_act(self):
        # ARRANGE #
        cases = {
            STEP__ACT__PARSE:
                {
                    EXECUTION__IMPLEMENTATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(parse_action=DO_RAISES_EXCEPTION),

                },
            STEP__VALIDATE_PRE_SDS:
                {
                    EXECUTION__VALIDATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            validate_pre_sds_action=SVH_VALIDATION_ERROR),

                    EXECUTION__HARD_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            validate_pre_sds_action=SVH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            validate_pre_sds_initial_action=DO_RAISES_EXCEPTION),
                },
        }
        test_case_definition = test_case_definition_for(instruction_set())

        test_case_source = ''

        for step, exit_value_2_constructor in cases.items():
            for exit_value, constructor in exit_value_2_constructor.items():
                expectation = Expectation(exit_value, output_is_empty)
                with self.subTest(step=step,
                                  exit_value=exit_value.exit_identifier):
                    # ACT & ASSERT #
                    _check(self,
                           test_case_definition,
                           constructor,
                           test_case_source,
                           self.sandbox_dir_resolver_that_should_not_be_called,
                           expectation)

    def test_before_assert(self):
        # ARRANGE #
        cases = {
            EXECUTION__VALIDATION_ERROR:
                before_assert_phase_instruction_that(validate_pre_sds=SVH_VALIDATION_ERROR),

            EXECUTION__HARD_ERROR:
                before_assert_phase_instruction_that(validate_pre_sds=SVH_HARD_ERROR),

            EXECUTION__IMPLEMENTATION_ERROR:
                before_assert_phase_instruction_that(validate_pre_sds_initial_action=DO_RAISES_EXCEPTION),
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_not_created_and_stdout_is_empty(phase_identifier.BEFORE_ASSERT, cases)

    def test_assert(self):
        # ARRANGE #
        cases = {
            EXECUTION__VALIDATION_ERROR:
                assert_phase_instruction_that(validate_pre_sds=SVH_VALIDATION_ERROR),

            EXECUTION__HARD_ERROR:
                assert_phase_instruction_that(validate_pre_sds=SVH_HARD_ERROR),

            EXECUTION__IMPLEMENTATION_ERROR:
                assert_phase_instruction_that(validate_pre_sds_initial_action=DO_RAISES_EXCEPTION),
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_not_created_and_stdout_is_empty(phase_identifier.ASSERT, cases)

    def test_cleanup(self):
        # ARRANGE #
        cases = {
            EXECUTION__VALIDATION_ERROR:
                cleanup_phase_instruction_that(validate_pre_sds=SVH_VALIDATION_ERROR),

            EXECUTION__HARD_ERROR:
                cleanup_phase_instruction_that(validate_pre_sds=SVH_HARD_ERROR),

            EXECUTION__IMPLEMENTATION_ERROR:
                cleanup_phase_instruction_that(validate_pre_sds_initial_action=DO_RAISES_EXCEPTION),
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_not_created_and_stdout_is_empty(phase_identifier.CLEANUP, cases)

    def _check_and_assert_sds_is_not_created_and_stdout_is_empty(self,
                                                                 phase: Phase,
                                                                 cases: Dict[ExitValue, TestCaseInstruction]):
        for exit_value, instruction in cases.items():
            case = Case(Arrangement(phase, instruction),
                        Expectation(exit_value,
                                    output_is_empty))
            with self.subTest(exit_identifier=exit_value.exit_identifier):
                _check_instruction(self,
                                   self.sandbox_dir_resolver_that_should_not_be_called,
                                   case)

    def sandbox_dir_resolver_that_should_not_be_called(self, dir_name: str) -> SandboxRootDirNameResolver:
        def ret_val():
            self.fail('SDS dir name resolver should not be called')
            return 'unused'

        return ret_val


class TestPhasesInPartialExecution(unittest.TestCase):
    def test_WHEN_pass_THEN_sds_SHOULD_be_printed(self):
        # ARRANGE #
        test_case_definition = test_case_definition_for(instruction_set())
        test_case_source = ''
        expectation = Expectation(EXECUTION__PASS, output_is_sds_which_should_be_preserved)
        # ACT & ASSERT #
        _check(self,
               test_case_definition,
               ActionToCheckExecutorParserThatRunsConstantActions(),
               test_case_source,
               self.sandbox_dir_resolver_of_given_dir,
               expectation)

    def test_setup(self):
        # ARRANGE #
        cases = {
            STEP__VALIDATE_POST_SETUP:
                {
                    EXECUTION__VALIDATION_ERROR:
                        setup_phase_instruction_that(validate_post_setup=SVH_VALIDATION_ERROR),

                    EXECUTION__HARD_ERROR:
                        setup_phase_instruction_that(validate_post_setup=SVH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        setup_phase_instruction_that(validate_post_setup_initial_action=DO_RAISES_EXCEPTION),
                },
            STEP__MAIN:
                {
                    EXECUTION__HARD_ERROR:
                        setup_phase_instruction_that(main=SH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        setup_phase_instruction_that(main_initial_action=DO_RAISES_EXCEPTION),
                },
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_preserved_and_is_printed(phase_identifier.SETUP, cases)

    def test_act(self):
        # ARRANGE #
        cases = {
            STEP__VALIDATE_POST_SETUP:
                {
                    EXECUTION__VALIDATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            validate_post_setup_action=SVH_VALIDATION_ERROR),

                    EXECUTION__HARD_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            validate_post_setup_action=SVH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            validate_post_setup_initial_action=DO_RAISES_EXCEPTION),

                },
            STEP__ACT__PREPARE:
                {
                    EXECUTION__HARD_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            prepare_action=SH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            prepare_initial_action=DO_RAISES_EXCEPTION),
                },
            STEP__ACT__EXECUTE:
                {
                    EXECUTION__IMPLEMENTATION_ERROR:
                        ActionToCheckExecutorParserThatRunsConstantActions(
                            execute_initial_action=DO_RAISES_EXCEPTION),
                },
        }
        test_case_definition = test_case_definition_for(instruction_set())

        test_case_source = ''

        for step, exit_value_2_constructor in cases.items():
            for exit_value, constructor in exit_value_2_constructor.items():
                expectation = Expectation(exit_value, output_is_sds_which_should_be_preserved)
                with self.subTest(step=step,
                                  exit_value=exit_value.exit_identifier):
                    # ACT & ASSERT #
                    _check(self,
                           test_case_definition,
                           constructor,
                           test_case_source,
                           self.sandbox_dir_resolver_of_given_dir,
                           expectation)

    def test_before_assert(self):
        # ARRANGE #
        cases = {
            STEP__VALIDATE_POST_SETUP:
                {
                    EXECUTION__VALIDATION_ERROR:
                        before_assert_phase_instruction_that(validate_post_setup=SVH_VALIDATION_ERROR),

                    EXECUTION__HARD_ERROR:
                        before_assert_phase_instruction_that(validate_post_setup=SVH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        before_assert_phase_instruction_that(
                            validate_post_setup_initial_action=DO_RAISES_EXCEPTION),

                },
            STEP__MAIN:
                {
                    EXECUTION__HARD_ERROR:
                        before_assert_phase_instruction_that(main=SH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        before_assert_phase_instruction_that(main_initial_action=DO_RAISES_EXCEPTION),
                },
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_preserved_and_is_printed(phase_identifier.BEFORE_ASSERT,
                                                               cases)

    def test_assert(self):
        # ARRANGE #
        cases = {
            STEP__VALIDATE_POST_SETUP:
                {
                    EXECUTION__VALIDATION_ERROR:
                        assert_phase_instruction_that(validate_post_setup=SVH_VALIDATION_ERROR),

                    EXECUTION__HARD_ERROR:
                        assert_phase_instruction_that(validate_post_setup=SVH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        assert_phase_instruction_that(validate_post_setup_initial_action=DO_RAISES_EXCEPTION),

                },
            STEP__MAIN:
                {
                    EXECUTION__FAIL:
                        assert_phase_instruction_that(main=do_return(pfh.new_pfh_fail('fail msg'))),

                    EXECUTION__HARD_ERROR:
                        assert_phase_instruction_that(main=do_return(pfh.new_pfh_hard_error('hard error msg'))),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        assert_phase_instruction_that(main_initial_action=DO_RAISES_EXCEPTION),
                },
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_preserved_and_is_printed(phase_identifier.ASSERT, cases)

    def test_cleanup(self):
        # ARRANGE #
        cases = {
            STEP__MAIN:
                {
                    EXECUTION__HARD_ERROR:
                        cleanup_phase_instruction_that(main=SH_HARD_ERROR),

                    EXECUTION__IMPLEMENTATION_ERROR:
                        cleanup_phase_instruction_that(main_initial_action=DO_RAISES_EXCEPTION),

                },
        }
        # ACT & ASSERT #
        self._check_and_assert_sds_is_preserved_and_is_printed(phase_identifier.CLEANUP, cases)

    def _check_and_assert_sds_is_preserved_and_is_printed(self,
                                                          phase: Phase,
                                                          cases: Dict[str, Dict[ExitValue, TestCaseInstruction]]):
        for step, exit_value_2_instructions in cases.items():
            for exit_value, instruction in exit_value_2_instructions.items():
                case = Case(Arrangement(phase, instruction),
                            Expectation(exit_value,
                                        output_is_sds_which_should_be_preserved))
                with self.subTest(step=step,
                                  exit_identifier=exit_value.exit_identifier):
                    _check_instruction(self,
                                       self.sandbox_dir_resolver_of_given_dir,
                                       case)

    @staticmethod
    def sandbox_dir_resolver_of_given_dir(dir_name: str) -> SandboxRootDirNameResolver:
        def ret_val():
            return dir_name

        return ret_val


def _check_instruction(put: unittest.TestCase,
                       mk_sds_resolver: Callable[[str], SandboxRootDirNameResolver],
                       case: Case):
    # ARRANGE #

    instruction_name = 'the_instruction'

    test_case_definition = test_case_definition_for(
        case.arrangement.instruction_setup_with_the_instruction(instruction_name))

    test_case_source = lines_content([
        section_header(case.arrangement.phase.identifier),
        instruction_name,
    ])

    _check(put,
           test_case_definition,
           ActionToCheckExecutorParserThatRunsConstantActions(),
           test_case_source,
           mk_sds_resolver,
           case.expectation)


def _check(put: unittest.TestCase,
           test_case_definition: TestCaseDefinitionForMainProgram,
           act_source_and_executor_constructor: ActionToCheckExecutorParser,
           test_case_source: str,
           mk_sds_resolver: Callable[[str], SandboxRootDirNameResolver],
           expectation: Expectation,
           ):
    # ARRANGE #

    case_file = File('the-test.case', test_case_source)
    source_files_dir_contents = DirContents([case_file])

    tc_handling_setup = TestCaseHandlingSetup(ActPhaseSetup(act_source_and_executor_constructor),
                                              IDENTITY_PREPROCESSOR)

    test_suite_definition = test_suite_definition_without_instructions()

    command_line_arguments = [
        OPTION_FOR_KEEPING_SANDBOX_DIRECTORY,
        case_file.name,
    ]

    # ACT #

    with tempfile.TemporaryDirectory() as dir_name:
        dir_name = resolved_path_name(dir_name)

        main_pgm = main_program_of(
            test_case_definition,
            test_suite_definition,
            tc_handling_setup,
            sandbox_root_dir_name_resolver=mk_sds_resolver(dir_name)
        )
        actual_result = capture_output_from_main_program__in_tmp_dir(command_line_arguments,
                                                                     source_files_dir_contents,
                                                                     main_pgm)

        # ASSERT #

        put.assertEqual(expectation.exit_vale.exit_code,
                        actual_result.exitcode,
                        'exit code')

        dir_and_stdout_assertion = expectation.output_assertion_for_sds_dir_name(dir_name)
        dir_and_stdout_assertion.apply_with_message(put, actual_result.stdout,
                                                    'dir and stdout')

        first_line_should_be_exit_identifier(put, actual_result.stderr, expectation.exit_vale)


def first_line_should_be_exit_identifier(put: unittest.TestCase,
                                         output: str,
                                         expected_exit_value: ExitValue):
    lines = output.split()
    put.assertTrue(len(lines) > 0,
                   'There should be at least one line (found {})'.format(len(lines)))

    first_line = lines[0]

    put.assertEqual(expected_exit_value.exit_identifier,
                    first_line,
                    'first line')


DO_RAISES_EXCEPTION = do_raise(ValueError('implementation error msg'))

SVH_VALIDATION_ERROR = do_return(svh.new_svh_validation_error('validation error msg'))
SVH_HARD_ERROR = do_return(svh.new_svh_hard_error('hard error msg'))

SH_HARD_ERROR = do_return(sh.new_sh_hard_error('hard error msg'))


def output_is_sds_which_should_be_preserved(sds_dir_name: str) -> ValueAssertion[str]:
    return asrt.and_([
        IsExistingDir(sds_dir_name),
        asrt.equals(sds_dir_name + '\n'),
    ])


def output_is_empty(sds_dir_name: str) -> ValueAssertion[str]:
    return asrt.equals('')


class IsExistingDir(ValueAssertionBase[Any]):
    def __init__(self, path_name: str):
        self.path_name = path_name

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        file_path = pathlib.Path(self.path_name)

        put.assertTrue(file_path.exists(),
                       message_builder.apply('Path should exist'))

        put.assertTrue(file_path.is_dir(),
                       message_builder.apply('Path should be a directory'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
