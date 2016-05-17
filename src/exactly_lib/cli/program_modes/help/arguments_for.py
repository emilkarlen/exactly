from exactly_lib.cli.program_modes.help.argument_parsing import INSTRUCTIONS, TEST_SUITE, TEST_CASE, HELP, \
    CONCEPT, HTML_DOCUMENTATION, SPECIFICATION
from exactly_lib.execution import phases
from exactly_lib.help.program_modes.test_case.config import phase_help_name


def program() -> list:
    return []


def html_doc() -> list:
    return [HTML_DOCUMENTATION]


def help_help() -> list:
    return [HELP]


def concept_list() -> list:
    return [CONCEPT]


def individual_concept(concept_name: str) -> list:
    return [CONCEPT] + concept_name.split()


def instructions() -> list:
    return [INSTRUCTIONS]


def phase(ph: phases.Phase) -> list:
    return phase_for_name(phase_help_name(ph))


def instruction_in_phase(phase_name: str,
                         instruction_name: str) -> list:
    return [phase_name, instruction_name]


def instruction_search(instruction_name: str) -> list:
    return [instruction_name]


def test_case_cli_syntax() -> list:
    return [TEST_CASE]


def test_case_specification() -> list:
    return [TEST_CASE, SPECIFICATION]


def test_suite_cli_syntax() -> list:
    return [TEST_SUITE]


def test_suite_specification() -> list:
    return [TEST_SUITE, SPECIFICATION]


def suite_section_for_name(section_name: str) -> list:
    return [TEST_SUITE, section_name]


def suite_instruction_in_section(section_name: str,
                                 instruction_name: str) -> list:
    return [TEST_SUITE, section_name, instruction_name]


def phase_for_name(phase_name: str) -> list:
    return [phase_name]
