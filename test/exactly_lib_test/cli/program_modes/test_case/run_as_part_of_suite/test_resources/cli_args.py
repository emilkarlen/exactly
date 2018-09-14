from typing import List

from exactly_lib.cli.definitions.program_modes.test_case import command_line_options


def cli_args_for_explicit_suite(suite_file: str, case_file: str) -> List[str]:
    return [command_line_options.OPTION_FOR_SUITE, suite_file, case_file]


def cli_args_for_implicit_default_suite(case_file: str) -> List[str]:
    return [case_file]
