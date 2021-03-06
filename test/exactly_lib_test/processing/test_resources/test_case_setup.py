from typing import Sequence, Tuple

from exactly_lib.common import instruction_name_and_argument_splitter
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.processors import TestCaseDefinition, Configuration
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.execution.test_resources import predefined_properties
from exactly_lib_test.processing.test_resources.act_phase import act_setup_that_does_nothing
from exactly_lib_test.processing.test_resources.act_phase import command_line_actor_setup


def test_case_handling_setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(command_line_actor_setup(),
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
        predefined_properties.new_empty(),
    )


def configuration_with_no_instructions_and_no_preprocessor() -> Configuration:
    return Configuration(test_case_definition_with_no_instructions_and_no_preprocessor(),
                         test_case_handling_setup(),
                         os_services_access.new_for_current_os(),
                         2 ** 10,
                         is_keep_sandbox=False)


def test_case_definition_with_only_assert_phase_instructions(
        assert_phase_instructions: Sequence[Tuple[str, AssertPhaseInstruction]]
) -> TestCaseDefinition:
    assert_phase_instructions_dict = {
        name: single_instruction_setup(name, instruction)
        for name, instruction in assert_phase_instructions
    }
    return TestCaseDefinition(
        TestCaseParsingSetup(
            instruction_name_extractor_function=instruction_name_and_argument_splitter.splitter,
            instruction_setup=InstructionsSetup(
                config_instruction_set={},
                setup_instruction_set={},
                assert_instruction_set=assert_phase_instructions_dict,
                before_assert_instruction_set={},
                cleanup_instruction_set={},
            ),
            act_phase_parser=ActPhaseParser()),
        predefined_properties.new_empty(),
    )
