from typing import List

from exactly_lib.cli.definitions.program_modes.test_case import command_line_options


def cli_args_for(suite_file: str, case_file: str) -> List[str]:
    return [command_line_options.OPTION_FOR_SUITE, suite_file, case_file]
