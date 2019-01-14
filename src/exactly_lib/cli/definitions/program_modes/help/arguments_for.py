from typing import List

from exactly_lib.cli.definitions.program_modes.help import command_line_options as clo
from exactly_lib.definitions.cross_ref.concrete_cross_refs import HelpPredefinedContentsPart
from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.definitions.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES, ACTOR_ENTITY_TYPE_NAMES, \
    SUITE_REPORTER_ENTITY_TYPE_NAMES, SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, TYPE_ENTITY_TYPE_NAMES, \
    BUILTIN_SYMBOL_ENTITY_TYPE_NAMES


def complete_help_for(help_arguments: List[str]) -> List[str]:
    return [clo.HELP] + help_arguments


def program() -> List[str]:
    return []


def html_doc() -> List[str]:
    return [clo.HTML_DOCUMENTATION]


def help_help() -> List[str]:
    return [clo.HELP]


def case_cli_syntax() -> List[str]:
    return [clo.TEST_CASE]


def case_specification() -> List[str]:
    return [clo.TEST_CASE, clo.SPECIFICATION]


def case_instructions() -> List[str]:
    return [clo.INSTRUCTIONS]


def case_phase_for_name(phase_name: str) -> List[str]:
    return [phase_name]


def case_instruction_in_phase(phase_name: str,
                              instruction_name: str) -> List[str]:
    return [phase_name, instruction_name]


def case_instructions_in_phase(phase_name: str) -> List[str]:
    return [phase_name, clo.INSTRUCTIONS]


def case_instruction_search(instruction_name: str) -> List[str]:
    return [instruction_name]


def suite_cli_syntax() -> List[str]:
    return [clo.TEST_SUITE]


def symbol_cli_syntax() -> List[str]:
    return [clo.SYMBOL]


def suite_specification() -> List[str]:
    return [clo.TEST_SUITE, clo.SPECIFICATION]


def suite_section_for_name(section_name: str) -> List[str]:
    return [clo.TEST_SUITE, section_name]


def suite_instruction_in_section(section_name: str,
                                 instruction_name: str) -> List[str]:
    return [clo.TEST_SUITE, section_name, instruction_name]


def entity_single(entity_type_name: str,
                  entity_name: str) -> List[str]:
    return [entity_type_name] + entity_name.split()


def concept_list() -> List[str]:
    return entity_help(CONCEPT_ENTITY_TYPE_NAMES)


def concept_single(concept_name: str) -> List[str]:
    return entity_help(CONCEPT_ENTITY_TYPE_NAMES,
                       concept_name)


def builtin(symbol_name: str = '') -> List[str]:
    return entity_help(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES, symbol_name)


def syntax_element(element: str = '') -> List[str]:
    return entity_help(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, element)


def symbol_type(type_name: str = '') -> List[str]:
    return entity_help(TYPE_ENTITY_TYPE_NAMES, type_name)


def actor_list() -> List[str]:
    return entity_help(ACTOR_ENTITY_TYPE_NAMES)


def actor_single(actor_name: str) -> List[str]:
    return entity_help(ACTOR_ENTITY_TYPE_NAMES,
                       actor_name)


def suite_reporter_list() -> List[str]:
    return entity_help(SUITE_REPORTER_ENTITY_TYPE_NAMES)


def suite_reporter_single(suite_reporter_name: str) -> List[str]:
    return entity_help(SUITE_REPORTER_ENTITY_TYPE_NAMES,
                       suite_reporter_name)


def entity_help(entity_type_names: EntityTypeNames,
                entity_name: str = '') -> List[str]:
    if entity_name:
        return [entity_type_names.identifier] + entity_name.split()
    else:
        return [entity_type_names.identifier]


ARGUMENTS_FOR_PART = {
    HelpPredefinedContentsPart.TEST_CASE_CLI: case_cli_syntax,
    HelpPredefinedContentsPart.TEST_SUITE_CLI: suite_cli_syntax,
    HelpPredefinedContentsPart.SYMBOL_CLI: symbol_cli_syntax,
    HelpPredefinedContentsPart.TEST_CASE_SPEC: case_specification,
    HelpPredefinedContentsPart.TEST_SUITE_SPEC: suite_specification,
}
