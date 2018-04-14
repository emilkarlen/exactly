from exactly_lib.act_phase_setups import command_line
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.processors import TestCaseDefinition, Configuration
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case import os_services
from exactly_lib_test.processing.test_resources.act_phase import act_setup_that_does_nothing


def test_case_handling_setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(command_line.act_phase_setup(),
                                 IdentityPreprocessor())


def setup_with_null_act_phase_and_null_preprocessing() -> TestCaseHandlingSetup:
    """
    Gives a setup with an act phase that does nothing, and without preprocessing.
    """
    return TestCaseHandlingSetup(
        act_phase_setup=act_setup_that_does_nothing(),
        preprocessor=IdentityPreprocessor(),
    )


def parsing_setup_with_no_instructions() -> TestCaseParsingSetup:
    return TestCaseParsingSetup(lambda x: '',
                                instruction_set_with_no_instructions(),
                                ActPhaseParser())


def instruction_set_with_no_instructions() -> InstructionsSetup:
    return InstructionsSetup({}, {}, {}, {}, {})


def test_case_definition_with_no_instructions_and_no_preprocessor() -> TestCaseDefinition:
    return TestCaseDefinition(
        parsing_setup_with_no_instructions(),
        PredefinedProperties(),
    )


def configuration_with_no_instructions_and_no_preprocessor() -> Configuration:
    return Configuration(test_case_definition_with_no_instructions_and_no_preprocessor(),
                         test_case_handling_setup(),
                         os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                         is_keep_sandbox=False)
