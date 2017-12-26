from exactly_lib.act_phase_setups import command_line
from exactly_lib.default.program_modes import test_suite
from exactly_lib.processing.instruction_setup import InstructionsSetup, TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite.suite_hierarchy_reading import Environment


def default_environment() -> Environment:
    return Environment(test_suite.new_parser(),
                       TestCaseParsingSetup(white_space_name_and_argument_splitter,
                                            empty_instruction_setup(),
                                            ActPhaseParser()),
                       TestCaseHandlingSetup(command_line.act_phase_setup(),
                                             IDENTITY_PREPROCESSOR))


def white_space_name_and_argument_splitter(s: str) -> str:
    return s.split()[0]


def empty_instruction_setup() -> InstructionsSetup:
    return InstructionsSetup(
        {},
        {},
        {},
        {},
        {})
