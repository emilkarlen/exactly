from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.entities.actors.entity_configuration import ACTOR_ENTITY_CONFIGURATION
from exactly_lib.help.entities.builtin.entity_configuration import builtin_symbols_entity_configuration
from exactly_lib.help.entities.concepts.entity_configuration import CONCEPT_ENTITY_CONFIGURATION
from exactly_lib.help.entities.configuration_parameters.entity_configuration import CONF_PARAM_ENTITY_CONFIGURATION
from exactly_lib.help.entities.suite_reporters.entity_configuration import SUITE_REPORTER_ENTITY_CONFIGURATION
from exactly_lib.help.entities.syntax_elements.entity_configuration import SYNTAX_ELEMENT_ENTITY_CONFIGURATION
from exactly_lib.help.entities.types.entity_configuration import TYPE_ENTITY_CONFIGURATION
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.help.program_modes.test_case.contents.phase import act, assert_, before_assert, configuration, \
    setup, cleanup
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.section.cases import CasesSectionDocumentation
from exactly_lib.help.program_modes.test_suite.section.configuration import ConfigurationSectionDocumentation
from exactly_lib.help.program_modes.test_suite.section.suites import SuitesSectionDocumentation
from exactly_lib.help_texts.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES, ACTOR_ENTITY_TYPE_NAMES, \
    CONF_PARAM_ENTITY_TYPE_NAMES, SUITE_REPORTER_ENTITY_TYPE_NAMES, SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, \
    TYPE_ENTITY_TYPE_NAMES, BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.help_texts.test_suite.section_names import SECTION_NAME__CONF, SECTION_NAME__SUITS, SECTION_NAME__CASES
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.test_case import phase_identifier


def new_application_help(instructions_setup: InstructionsSetup,
                         suite_configuration_section_instructions: dict,
                         builtin_symbol_documentation_list: list = ()) -> ApplicationHelp:
    """
    :param builtin_symbol_documentation_list: [`BuiltinSymbolDocumentation`]
    :param instructions_setup: Test case instruction set
    :param suite_configuration_section_instructions: instruction-name -> `SingleInstructionSetup`
    """
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp(phase_helps_for(instructions_setup)),
                           test_suite_help(suite_configuration_section_instructions),
                           entity_name_2_entity_configuration(list(builtin_symbol_documentation_list)))


def entity_name_2_entity_configuration(builtin_symbol_documentation_list: list):
    return {
        CONCEPT_ENTITY_TYPE_NAMES.identifier: CONCEPT_ENTITY_CONFIGURATION,

        CONF_PARAM_ENTITY_TYPE_NAMES.identifier: CONF_PARAM_ENTITY_CONFIGURATION,

        ACTOR_ENTITY_TYPE_NAMES.identifier: ACTOR_ENTITY_CONFIGURATION,

        SUITE_REPORTER_ENTITY_TYPE_NAMES.identifier: SUITE_REPORTER_ENTITY_CONFIGURATION,

        TYPE_ENTITY_TYPE_NAMES.identifier: TYPE_ENTITY_CONFIGURATION,

        SYNTAX_ELEMENT_ENTITY_TYPE_NAMES.identifier: SYNTAX_ELEMENT_ENTITY_CONFIGURATION,

        BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.identifier: builtin_symbols_entity_configuration(
            builtin_symbol_documentation_list),
    }


def test_suite_help(configuration_section_instructions: dict) -> TestSuiteHelp:
    """
    :param configuration_section_instructions: instruction-name -> `SingleInstructionSetup`
    """
    return TestSuiteHelp([
        ConfigurationSectionDocumentation(SECTION_NAME__CONF,
                                          instruction_set_help(configuration_section_instructions)),
        CasesSectionDocumentation(SECTION_NAME__CASES),
        SuitesSectionDocumentation(SECTION_NAME__SUITS),
    ])


def phase_helps_for(instructions_setup: InstructionsSetup) -> iter:
    return [
        configuration.ConfigurationPhaseDocumentation(phase_help_name(phase_identifier.CONFIGURATION),
                                                      instruction_set_help(
                                                          instructions_setup.config_instruction_set)),
        setup.SetupPhaseDocumentation(phase_help_name(phase_identifier.SETUP),
                                      instruction_set_help(instructions_setup.setup_instruction_set)),
        act.ActPhaseDocumentation(phase_help_name(phase_identifier.ACT)),
        before_assert.BeforeAssertPhaseDocumentation(phase_help_name(phase_identifier.BEFORE_ASSERT),
                                                     instruction_set_help(
                                                         instructions_setup.before_assert_instruction_set)),
        assert_.AssertPhaseDocumentation(phase_help_name(phase_identifier.ASSERT),
                                         instruction_set_help(instructions_setup.assert_instruction_set)),
        cleanup.CleanupPhaseDocumentation(phase_help_name(phase_identifier.CLEANUP),
                                          instruction_set_help(instructions_setup.cleanup_instruction_set)),
    ]


def instruction_set_help(single_instruction_setup_dic: dict) -> SectionInstructionSet:
    return SectionInstructionSet(map(lambda x: x.documentation, single_instruction_setup_dic.values()))
