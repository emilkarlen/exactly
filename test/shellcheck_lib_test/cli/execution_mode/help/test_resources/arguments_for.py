from shellcheck_lib.cli.execution_mode.help.argument_parsing import INSTRUCTIONS, SUITE
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.help.config import phase_help_name


def program() -> list:
    return []


def instructions() -> list:
    return [INSTRUCTIONS]


def phase(ph: phases.Phase) -> list:
    return phase_for_name(phase_help_name(ph))


def instruction_in_phase(phase_name: str,
                         instruction_name: str) -> list:
    return [phase_name, instruction_name]


def instruction_search(instruction_name: str) -> list:
    return [instruction_name]


def suite() -> list:
    return [SUITE]


def suite_section(section_name: str) -> list:
    return [SUITE, section_name]


def phase_for_name(phase_name: str) -> list:
    return [phase_name]
