from exactly_lib.default.instruction_name_and_argument_splitter import \
    splitter as default_splitter
from exactly_lib.default.program_modes.test_case import builtin_symbols, test_case_handling_setup
from exactly_lib.default.program_modes.test_case.default_instructions_setup import INSTRUCTIONS_SETUP
from exactly_lib.default.program_modes.test_suite import test_suite_definition
from exactly_lib_test.cli.test_resources.internal_main_program_runner import RunViaMainProgramInternally


def main_program_runner_with_default_setup__in_same_process() -> RunViaMainProgramInternally:
    return RunViaMainProgramInternally(the_test_case_handling_setup=test_case_handling_setup.setup(),
                                       instructions_setup=INSTRUCTIONS_SETUP,
                                       test_suite_definition=test_suite_definition(),
                                       name_and_argument_splitter=default_splitter,
                                       builtin_symbols=builtin_symbols.ALL,
                                       )
