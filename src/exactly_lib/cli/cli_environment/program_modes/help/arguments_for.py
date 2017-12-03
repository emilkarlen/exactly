from exactly_lib.cli.cli_environment.program_modes.help import command_line_options as clo
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.help_texts.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES, ACTOR_ENTITY_TYPE_NAMES, \
    SUITE_REPORTER_ENTITY_TYPE_NAMES, SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, TYPE_ENTITY_TYPE_NAMES, \
    BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.test_case import phase_identifier


def complete_help_for(help_arguments: list) -> list:
    return [clo.HELP] + help_arguments


def program() -> list:
    return []


def html_doc() -> list:
    return [clo.HTML_DOCUMENTATION]


def help_help() -> list:
    return [clo.HELP]


def case_cli_syntax() -> list:
    return [clo.TEST_CASE]


def case_specification() -> list:
    return [clo.TEST_CASE, clo.SPECIFICATION]


def case_instructions() -> list:
    return [clo.INSTRUCTIONS]


def case_phase(ph: phase_identifier.Phase) -> list:
    return case_phase_for_name(phase_help_name(ph))


def case_phase_for_name(phase_name: str) -> list:
    return [phase_name]


def case_instruction_in_phase(phase_name: str,
                              instruction_name: str) -> list:
    return [phase_name, instruction_name]


def case_instructions_in_phase(phase_name: str) -> list:
    return [phase_name, clo.INSTRUCTIONS]


def case_instruction_search(instruction_name: str) -> list:
    return [instruction_name]


def suite_cli_syntax() -> list:
    return [clo.TEST_SUITE]


def suite_specification() -> list:
    return [clo.TEST_SUITE, clo.SPECIFICATION]


def suite_section_for_name(section_name: str) -> list:
    return [clo.TEST_SUITE, section_name]


def suite_instruction_in_section(section_name: str,
                                 instruction_name: str) -> list:
    return [clo.TEST_SUITE, section_name, instruction_name]


def entity_single(entity_type_name: str,
                  entity_name: str) -> list:
    return [entity_type_name] + entity_name.split()


def concept_list() -> list:
    return entity_help(CONCEPT_ENTITY_TYPE_NAMES)


def concept_single(concept_name: str) -> list:
    return entity_help(CONCEPT_ENTITY_TYPE_NAMES,
                       concept_name)


def builtin(symbol_name: str = '') -> list:
    return entity_help(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES, symbol_name)


def syntax_element(element: str = '') -> list:
    return entity_help(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, element)


def symbol_type(type_name: str = '') -> list:
    return entity_help(TYPE_ENTITY_TYPE_NAMES, type_name)


def actor_list() -> list:
    return entity_help(ACTOR_ENTITY_TYPE_NAMES)


def actor_single(actor_name: str) -> list:
    return entity_help(ACTOR_ENTITY_TYPE_NAMES,
                       actor_name)


def suite_reporter_list() -> list:
    return entity_help(SUITE_REPORTER_ENTITY_TYPE_NAMES)


def suite_reporter_single(suite_reporter_name: str) -> list:
    return entity_help(SUITE_REPORTER_ENTITY_TYPE_NAMES,
                       suite_reporter_name)


def entity_help(entity_type_names: EntityTypeNames,
                entity_name: str = '') -> list:
    if entity_name:
        return [entity_type_names.identifier] + entity_name.split()
    else:
        return [entity_type_names.identifier]
