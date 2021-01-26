import unittest

from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_case.phase_names_plain import ACT_PHASE_NAME, ASSERT_PHASE_NAME, SETUP_PHASE_NAME
from exactly_lib.processing import exit_values
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.impls.instructions.setup import stdin as setup_stdin_abs_stx
from exactly_lib_test.impls.types.string_matcher.test_resources import abstract_syntaxes as sm_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.section_document.test_resources.abstract_syntax import SectionHeaderAbStx, NamedInstruction
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResultInfo
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.source import abs_stx_utils
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import RelOptPathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as program_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(
        [
            StdinOfActPhaseShouldBeEmptyWhenNotSetInSetupPhase(),
            StdinOfActPhaseShouldBeValueSetInSetupPhase(),
            StdinOfActPhaseShouldBeLastValueSetInSetupPhaseWhenSetMultipleTimes(),
            ResultShouldBeHardErrorWhenSetupPhaseSetsStdinToNonExistingFileInSds(),
            StdinShouldBeValidWhen1stSetToInvalidBut2ndSetToValidInSetupPhaseWhenSetMultipleTimes(),
        ],
        main_program_runner
    )


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


class StdinOfActPhaseShouldBeEmptyWhenNotSetInSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        return abs_stx_utils.of_lines([
            SectionHeaderAbStx(ACT_PHASE_NAME),
            _PROGRAM_THAT_COPIES_STDIN_2_STDOUT,

            SectionHeaderAbStx(ASSERT_PHASE_NAME),
            _stdout_equals(''),
        ])


class StdinOfActPhaseShouldBeValueSetInSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        stdin_set_in_setup = 'the contents of stdin'

        return abs_stx_utils.of_lines([
            SectionHeaderAbStx(SETUP_PHASE_NAME),
            _set_stdin_to_str(stdin_set_in_setup),

            SectionHeaderAbStx(ACT_PHASE_NAME),
            _PROGRAM_THAT_COPIES_STDIN_2_STDOUT,

            SectionHeaderAbStx(ASSERT_PHASE_NAME),
            _stdout_equals(stdin_set_in_setup),
        ])


class StdinOfActPhaseShouldBeLastValueSetInSetupPhaseWhenSetMultipleTimes(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        stdin_set_in_setup__first = 'the contents of stdin, set first'
        stdin_set_in_setup__last = 'the contents of stdin, set last'

        return abs_stx_utils.of_lines([
            SectionHeaderAbStx(SETUP_PHASE_NAME),
            _set_stdin_to_str(stdin_set_in_setup__first),
            _set_stdin_to_str(stdin_set_in_setup__last),

            SectionHeaderAbStx(ACT_PHASE_NAME),
            _PROGRAM_THAT_COPIES_STDIN_2_STDOUT,

            SectionHeaderAbStx(ASSERT_PHASE_NAME),
            _stdout_equals(stdin_set_in_setup__last),
        ])


class StdinShouldBeValidWhen1stSetToInvalidBut2ndSetToValidInSetupPhaseWhenSetMultipleTimes(
    SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        valid_stdin_contents = 'valid contents of stdin'

        return abs_stx_utils.of_lines([
            SectionHeaderAbStx(SETUP_PHASE_NAME),
            _set_stdin_to_file(
                RelOptPathAbsStx(RelOptionType.REL_ACT,
                                 'non-existing-file')
            ),
            _set_stdin_to_str(valid_stdin_contents),

            SectionHeaderAbStx(ACT_PHASE_NAME),
            _PROGRAM_THAT_COPIES_STDIN_2_STDOUT,

            SectionHeaderAbStx(ASSERT_PHASE_NAME),
            _stdout_equals(valid_stdin_contents),
        ])


class ResultShouldBeHardErrorWhenSetupPhaseSetsStdinToNonExistingFileInSds(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__HARD_ERROR)

    def test_case(self) -> str:
        return abs_stx_utils.of_lines([
            SectionHeaderAbStx(SETUP_PHASE_NAME),
            _set_stdin_to_file(
                RelOptPathAbsStx(RelOptionType.REL_ACT,
                                 'non-existing-file')
            ),
        ])


_PROGRAM_THAT_COPIES_STDIN_2_STDOUT = program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
    py_programs.copy_stdin_to__single_line(ProcOutputFile.STDOUT)
)


def _stdout_equals(expected: str) -> AbstractSyntax:
    return NamedInstruction(
        instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
        sm_abs_stx.EqualsAbsStx(
            str_abs_stx.StringLiteralAbsStx(expected, QuoteType.HARD),
        )
    )


def _set_stdin_to_str(contents: str) -> AbstractSyntax:
    return _set_stdin(str_src_abs_stx.StringSourceOfStringAbsStx.of_str(contents, QuoteType.HARD))


def _set_stdin_to_file(file: PathAbsStx) -> AbstractSyntax:
    return _set_stdin(str_src_abs_stx.StringSourceOfFileAbsStx(file))


def _set_stdin(contents: StringSourceAbsStx) -> AbstractSyntax:
    return NamedInstruction(
        instruction_names.CONTENTS_OF_STDIN_INSTRUCTION_NAME,
        setup_stdin_abs_stx.InstructionAbsStx(contents)
    )


PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0 = lines_content(['import sys',
                                                          'sys.exit(0)'])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
