from typing import List

from exactly_lib.cli.definitions.common_cli_options import SYMBOL_COMMAND
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options


def arguments(symbol_arguments: List[str]) -> List[str]:
    return [SYMBOL_COMMAND] + symbol_arguments


def explicit_suite_part(suite_file_name: str) -> List[str]:
    return [
        command_line_options.OPTION_FOR_SUITE,
        suite_file_name,
    ]


def explicit_suite_and_case(suite_file_name: str,
                            case_file_name: str) -> List[str]:
    return explicit_suite_part(suite_file_name) + [
        case_file_name,
    ]
