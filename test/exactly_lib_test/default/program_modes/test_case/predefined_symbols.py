import pathlib
import unittest
from abc import ABC
from typing import List

from exactly_lib.default.program_modes.test_case.builtin_symbols import strings
from exactly_lib.default.program_modes.test_case.builtin_symbols import test_case_dir_symbols, string_transformers
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.processing import exit_values
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.default.test_resources.actors import SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as str_matcher_args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.process import SubProcessResultInfo
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite_that_requires_main_program_runner_with_default_setup(main_program_runner) -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(_TESTS, main_program_runner)


class AllBuiltinStringSymbolsShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it = [
            args.symbol_def_instruction(builtin_symbol.container.value_type,
                                        'COPY_OF_' + builtin_symbol.name,
                                        symbol_reference_syntax_for_name(builtin_symbol.name)).as_str
            for builtin_symbol in strings.all_strings()
        ]

        return lines_content(
            [phase_header_line(phase_identifier.SETUP)] +

            one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it
        )


class AllPredefinedTestCaseDirSymbolsShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it = [
            args.symbol_def_instruction(builtin_symbol.container.value_type,
                                        'COPY_OF_' + builtin_symbol.name,
                                        symbol_reference_syntax_for_name(builtin_symbol.name)).as_str
            for builtin_symbol in test_case_dir_symbols.ALL
        ]

        return lines_content(
            [phase_header_line(phase_identifier.SETUP)] +

            one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it
        )


class AllBuiltinStringTransformerSymbolsShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def test_case(self) -> str:
        one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it = [
            args.symbol_def_instruction(builtin_symbol.container.value_type,
                                        'COPY_OF_' + builtin_symbol.name,
                                        symbol_reference_syntax_for_name(builtin_symbol.name)).as_str
            for builtin_symbol in string_transformers.ALL
        ]

        return lines_content(
            [phase_header_line(phase_identifier.SETUP)] +

            one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it
        )


class TestStringValueEqualsBuiltinBase(SetupWithoutPreprocessorAndDefaultActor, ABC):
    PY_PROGRAM_FILE_NAME = 'write-expected-to-stdout.py'

    def __init__(self,
                 py_pgm_that_writes_expected_to_stdout: str,
                 name_of_checked_symbol: str,
                 ):
        self._py_pgm_that_writes_expected_to_stdout = py_pgm_that_writes_expected_to_stdout
        self._name_of_checked_symbol = name_of_checked_symbol

    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> List[FileSystemElement]:
        return [
            file_structure.File(
                self.PY_PROGRAM_FILE_NAME,
                self._py_pgm_that_writes_expected_to_stdout
            ),
        ]

    def test_case(self) -> str:
        equals_builtin_symbol_value_matcher = str_matcher_args.Equals(
            symbol_reference_syntax_for_name(self._name_of_checked_symbol)
        ).as_arguments.as_single_string

        return lines_content([
            pgm_args.interpret_py_source_file(self.PY_PROGRAM_FILE_NAME).as_str,

            phase_header_line(phase_identifier.ASSERT),

            ' '.join((instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
                      equals_builtin_symbol_value_matcher)),
        ])


class TestLineSepStringValue(TestStringValueEqualsBuiltinBase):
    def __init__(self):
        super().__init__(py_programs.py_pgm_that_writes_os_linesep_to_stdout(),
                         strings.LINE_SEP)


class TestTabCharacterStringValue(TestStringValueEqualsBuiltinBase):
    def __init__(self):
        super().__init__(py_programs.py_pgm_that_writes_tab_character_to_stdout(),
                         strings.TAB)


class TheTestCaseDirReplacementTransformerShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    name_of_source_file_to_interpret = 'system-under-test.py'

    def expected_result(self) -> ValueAssertion[SubProcessResultInfo]:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> List[FileSystemElement]:
        return [
            file_structure.File(self.name_of_source_file_to_interpret,
                                PYTHON_PROGRAM_THAT_PRINTS_THE_CURRENT_DIRECTORY)
        ]

    def test_case(self) -> str:
        return lines_content(
            [
                phase_header_line(phase_identifier.CONFIGURATION),

                SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER,

                phase_header_line(phase_identifier.ACT),

                self.name_of_source_file_to_interpret,

                phase_header_line(phase_identifier.ASSERT),

                '{stdout} {transform_by_pre_def_replacement_of_test_case_dirs} {equals} <<EOF'.format(
                    stdout=instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
                    transform_by_pre_def_replacement_of_test_case_dirs=
                    argument_syntax.syntax_for_transformer_option(
                        string_transformers.EXACTLY_TEST_CASE_DIRS_REPLACEMENT),
                    equals=matcher_options.EQUALS_ARGUMENT,
                ),
                test_case_dir_symbols.SYMBOL_ACT.name,
                'EOF',
            ])


PYTHON_PROGRAM_THAT_PRINTS_THE_CURRENT_DIRECTORY = lines_content(['import pathlib',
                                                                  'print(pathlib.Path.cwd())'])

_TESTS = [
    AllBuiltinStringSymbolsShouldBeAvailableInTheSetupPhase(),
    AllPredefinedTestCaseDirSymbolsShouldBeAvailableInTheSetupPhase(),
    AllBuiltinStringTransformerSymbolsShouldBeAvailableInTheSetupPhase(),
    TestLineSepStringValue(),
    TestTabCharacterStringValue(),
    TheTestCaseDirReplacementTransformerShouldBeAvailableInTheSetupPhase(),
]


def _suite_for_run_via_main_program_with_default_setup__in_same_process() -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(_TESTS, main_program_runner_with_default_setup__in_same_process())


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite_for_run_via_main_program_with_default_setup__in_same_process())
