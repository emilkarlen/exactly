from exactly_lib.cli.cli_environment.program_modes.help.command_line_options import \
    INSTRUCTIONS, TEST_SUITE, TEST_CASE, CONCEPT, HTML_DOCUMENTATION, SPECIFICATION, ACTOR, SUITE_REPORTER, HELP
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.test_case import phase_identifier


def complete_help_for(help_arguments: list) -> list:
    return [HELP] + help_arguments


def program() -> list:
    return []


def html_doc() -> list:
    return [HTML_DOCUMENTATION]


def help_help() -> list:
    return [HELP]


def case_cli_syntax() -> list:
    return [TEST_CASE]


def case_specification() -> list:
    return [TEST_CASE, SPECIFICATION]


def case_instructions() -> list:
    return [INSTRUCTIONS]


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
    return [TEST_SUITE]


def suite_specification() -> list:
    return [TEST_SUITE, SPECIFICATION]


def suite_section_for_name(section_name: str) -> list:
    return [TEST_SUITE, section_name]


def suite_instruction_in_section(section_name: str,
                                 instruction_name: str) -> list:
    return [TEST_SUITE, section_name, instruction_name]


def entity_single(entity_type_name: str,
                  entity_name: str) -> list:
    return [entity_type_name] + entity_name.split()


def concept_list() -> list:
    return [CONCEPT]


def concept_single(concept_name: str) -> list:
    return [CONCEPT] + concept_name.split()


def actor_list() -> list:
    return [ACTOR]


def actor_single(actor_name: str) -> list:
    return [ACTOR] + actor_name.split()


def suite_reporter_list() -> list:
    return [SUITE_REPORTER]


def suite_reporter_single(suite_reporter_name: str) -> list:
    return [SUITE_REPORTER] + suite_reporter_name.split()
