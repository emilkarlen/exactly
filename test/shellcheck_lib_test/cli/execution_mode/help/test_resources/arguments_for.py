from shellcheck_lib.cli.program_modes.help.argument_parsing import INSTRUCTIONS, TEST_SUITE, TEST_CASE, HELP
from shellcheck_lib.execution import phases
from shellcheck_lib.help.program_modes.test_case.config import phase_help_name


def program() -> list:
    return []


def help_help() -> list:
    return [HELP]


def instructions() -> list:
    return [INSTRUCTIONS]


def phase(ph: phases.Phase) -> list:
    return phase_for_name(phase_help_name(ph))


def instruction_in_phase(phase_name: str,
                         instruction_name: str) -> list:
    return [phase_name, instruction_name]


def instruction_search(instruction_name: str) -> list:
    return [instruction_name]


def test_case() -> list:
    return [TEST_CASE]


def suite() -> list:
    return [TEST_SUITE]


def suite_section(section_name: str) -> list:
    return [TEST_SUITE, section_name]


def phase_for_name(phase_name: str) -> list:
    return [phase_name]
