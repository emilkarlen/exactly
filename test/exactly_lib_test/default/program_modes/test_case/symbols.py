import pathlib
import unittest

from exactly_lib.default.program_modes.test_case import execution_properties
from exactly_lib.execution import exit_values
from exactly_lib.help_texts.test_case.instructions import assign_symbol
from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.string import lines_content
from exactly_lib_test.default.program_modes.test_case.act_phase import PYTHON_PROGRAM_THAT_EXISTS_WITH_STATUS_0
from exactly_lib_test.default.test_resources.actors import SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.default.test_resources.test_case_file_elements import phase_header_line
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_without_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_check_for_test_case import \
    SetupWithoutPreprocessorAndDefaultActor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.process_result_info_assertions import \
    process_result_for_exit_value


def suite_that_requires_main_program_runner_with_default_setup(main_program_runner) -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(_TESTS, main_program_runner)


class AllPredefinedSymbolsShouldBeAvailableInTheSetupPhase(SetupWithoutPreprocessorAndDefaultActor):
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
                def_instruction=SYMBOL_DEFINITION_INSTRUCTION_NAME,
                path_type=assign_symbol.PATH_TYPE,
                name_to_define='COPY_OF_' + symbol.key,
                reference_to_predefined_symbol=symbol_reference_syntax_for_name(symbol.key))
            for symbol in execution_properties.ALL
        ]

        return lines_content(
            [phase_header_line(phase_identifier.CONFIGURATION)] +

            [SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER] +

            [phase_header_line(phase_identifier.SETUP)] +

            one_line_per_predefined_symbol__that_defines_one_symbol_in_terms_of_it +

            [phase_header_line(phase_identifier.ACT)] +

            [self.name_of_source_file_to_interpret],
        )


_TESTS = [
    AllPredefinedSymbolsShouldBeAvailableInTheSetupPhase(),
]


def _suite_for_run_via_main_program_with_default_setup__in_same_process() -> unittest.TestSuite:
    return tests_for_setup_without_preprocessor(_TESTS, main_program_runner_with_default_setup__in_same_process())


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite_for_run_via_main_program_with_default_setup__in_same_process())
