from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options


def cli_args_for(suite_file: str, case_file: str) -> list:
    return [command_line_options.OPTION_FOR_SUITE, suite_file, case_file]
