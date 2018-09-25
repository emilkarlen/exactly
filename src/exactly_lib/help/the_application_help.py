from typing import Sequence, Dict, List

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES, ACTOR_ENTITY_TYPE_NAMES, \
    CONF_PARAM_ENTITY_TYPE_NAMES, SUITE_REPORTER_ENTITY_TYPE_NAMES, SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, \
    TYPE_ENTITY_TYPE_NAMES, BUILTIN_SYMBOL_ENTITY_TYPE_NAMES, DIRECTIVE_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.entities.actors.entity_configuration import ACTOR_ENTITY_CONFIGURATION
from exactly_lib.help.entities.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.help.entities.builtin.entity_configuration import builtin_symbols_entity_configuration
from exactly_lib.help.entities.concepts.entity_configuration import CONCEPT_ENTITY_CONFIGURATION
from exactly_lib.help.entities.configuration_parameters.entity_configuration import CONF_PARAM_ENTITY_CONFIGURATION
from exactly_lib.help.entities.directives.entity_configuration import DIRECTIVE_ENTITY_CONFIGURATION
from exactly_lib.help.entities.suite_reporters.entity_configuration import SUITE_REPORTER_ENTITY_CONFIGURATION
from exactly_lib.help.entities.syntax_elements.entity_configuration import SYNTAX_ELEMENT_ENTITY_CONFIGURATION
from exactly_lib.help.entities.types.entity_configuration import TYPE_ENTITY_CONFIGURATION
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.the_test_case_help import test_case_help
from exactly_lib.help.program_modes.test_suite.the_test_suite_help import test_suite_help
from exactly_lib.processing.instruction_setup import InstructionsSetup


def new_application_help(instructions_setup: InstructionsSetup,
                         suite_configuration_section_instructions: Dict[str, SingleInstructionSetup],
                         builtin_symbols: Sequence[BuiltinSymbolDocumentation] = ()
                         ) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           test_case_help(instructions_setup),
                           test_suite_help(suite_configuration_section_instructions),
                           entity_name_2_entity_configuration(list(builtin_symbols)))


def entity_name_2_entity_configuration(builtin_symbols: List[BuiltinSymbolDocumentation]
                                       ) -> Dict[str, EntityTypeConfiguration]:
    return {
        CONCEPT_ENTITY_TYPE_NAMES.identifier: CONCEPT_ENTITY_CONFIGURATION,

        CONF_PARAM_ENTITY_TYPE_NAMES.identifier: CONF_PARAM_ENTITY_CONFIGURATION,

        ACTOR_ENTITY_TYPE_NAMES.identifier: ACTOR_ENTITY_CONFIGURATION,

        SUITE_REPORTER_ENTITY_TYPE_NAMES.identifier: SUITE_REPORTER_ENTITY_CONFIGURATION,

        TYPE_ENTITY_TYPE_NAMES.identifier: TYPE_ENTITY_CONFIGURATION,

        SYNTAX_ELEMENT_ENTITY_TYPE_NAMES.identifier: SYNTAX_ELEMENT_ENTITY_CONFIGURATION,

        DIRECTIVE_ENTITY_TYPE_NAMES.identifier: DIRECTIVE_ENTITY_CONFIGURATION,

        BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.identifier: builtin_symbols_entity_configuration(
            builtin_symbols),
    }
