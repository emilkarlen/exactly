import pathlib

from shellcheck_lib.cli.cli_environment.exit_value import ExitValue


def suite_begin(file_path: pathlib.Path) -> str:
    return 'suite ' + str(file_path) + ': begin'


def suite_end(file_path: pathlib.Path) -> str:
    return 'suite ' + str(file_path) + ': end'


def case(file_path: pathlib.Path, status: str) -> str:
    return 'case  ' + str(file_path) + ': ' + status


def summary_for_invalid_suite(file_path: pathlib.Path, exit_value: ExitValue) -> list:
    return [exit_value.exit_identifier]


def summary_for_valid_suite(file_path: pathlib.Path,
                            exit_value: ExitValue) -> list:
    """
    :type errors: dict ExitValue -> int
    """
    return [exit_value.exit_identifier]
