import pathlib
import unittest

from exactly_lib.default.program_modes.test_case.builtin_symbols import test_case_dir_symbols, lines_transformers
from exactly_lib.help_texts.entity.types import PATH_CONCEPT_INFO
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.processing import exit_values
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.program_modes.test_case.act_phase import PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0
from exactly_lib_test.default.test_resources.actors import SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import argument_syntax
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value


def suite_that_requires_main_program_runner_with_default_setup(main_program_runner) -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(_TESTS, main_program_runner)


class AllPredefinedTestCaseDirSymbolsShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    name_of_source_file_to_interpret = 'system-under-test.py'

    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> list:
        return [
            file_structure.File(self.name_of_source_file_to_interpret,
                                PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0)
        ]

    def test_case(self) -> str:
        one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it = [
            '{def_instruction} {path_type} {name_to_define} = {reference_to_predefined_symbol}'.format(
                def_instruction=instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,
                path_type=PATH_CONCEPT_INFO.identifier,
                name_to_define='COPY_OF_' + builtin_symbol.name,
                reference_to_predefined_symbol=symbol_reference_syntax_for_name(builtin_symbol.name))
            for builtin_symbol in test_case_dir_symbols.ALL
        ]

        return lines_content(
            [phase_header_line(phase_identifier.CONFIGURATION)] +

            [SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER] +

            [phase_header_line(phase_identifier.SETUP)] +

            one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it +

            [phase_header_line(phase_identifier.ACT)] +

            [self.name_of_source_file_to_interpret],
        )


class TheTestCaseDirReplacementTransformerShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
    name_of_source_file_to_interpret = 'system-under-test.py'

    def expected_result(self) -> asrt.ValueAssertion:
        return process_result_for_exit_value(exit_values.EXECUTION__PASS)

    def _additional_files_in_file_structure(self, root_path: pathlib.Path) -> list:
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
                        lines_transformers.EXACTLY_TEST_CASE_DIRS_REPLACEMENT),
                    equals=instruction_options.EQUALS_ARGUMENT,
                ),
                test_case_dir_symbols.SYMBOL_ACT.name,
                'EOF',
            ])


PYTHON_PROGRAM_THAT_PRINTS_THE_CURRENT_DIRECTORY = lines_content(['import pathlib',
                                                                  'print(pathlib.Path.cwd())'])

_TESTS = [
    AllPredefinedTestCaseDirSymbolsShouldBeAvailableInTheSetupPhase(),
    TheTestCaseDirReplacementTransformerShouldBeAvailableInTheSetupPhase(),
]


def _suite_for_run_via_main_program_with_default_setup__in_same_process() -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(_TESTS, main_program_runner_with_default_setup__in_same_process())


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite_for_run_via_main_program_with_default_setup__in_same_process())
