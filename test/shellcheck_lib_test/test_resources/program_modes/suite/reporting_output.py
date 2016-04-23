import pathlib

from shellcheck_lib.cli.cli_environment.exit_value import ExitValue


def suite_begin(file_path: pathlib.Path) -> str:
    return 'SUITE ' + str(file_path) + ': BEGIN'


def suite_end(file_path: pathlib.Path) -> str:
    return 'SUITE ' + str(file_path) + ': END'


def case(file_path: pathlib.Path, status: str) -> str:
    return 'CASE  ' + str(file_path) + ': ' + status


def summary(file_path: pathlib.Path, exit_value: ExitValue) -> list:
    return []
