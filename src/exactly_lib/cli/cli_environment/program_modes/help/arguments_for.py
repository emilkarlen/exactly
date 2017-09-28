from exactly_lib.cli.cli_environment.program_modes.help import command_line_options as clo
from exactly_lib.help.program_modes.test_case.config import phase_help_name
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
    return [clo.CONCEPT]


def concept_single(concept_name: str) -> list:
    return [clo.CONCEPT] + concept_name.split()


def builtin(symbol_name: str = '') -> list:
    if symbol_name:
        return [clo.BUILTIN, symbol_name]
    else:
        return [clo.BUILTIN]


def syntax(syntax_element: str = '') -> list:
    if syntax_element:
        return [clo.SYNTAX, syntax_element]
    else:
        return [clo.SYNTAX]


def symbol_type(type_name: str = '') -> list:
    if type_name:
        return [clo.TYPE, type_name]
    else:
        return [clo.TYPE]


def actor_list() -> list:
    return [clo.ACTOR]


def actor_single(actor_name: str) -> list:
    return [clo.ACTOR] + actor_name.split()


def suite_reporter_list() -> list:
    return [clo.SUITE_REPORTER]


def suite_reporter_single(suite_reporter_name: str) -> list:
    return [clo.SUITE_REPORTER] + suite_reporter_name.split()
