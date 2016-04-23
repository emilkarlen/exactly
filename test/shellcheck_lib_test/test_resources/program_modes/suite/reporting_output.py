import pathlib

from shellcheck_lib.cli.cli_environment.exit_value import ExitValue


def suite_begin(file_path: pathlib.Path) -> str:
    return 'SUITE ' + str(file_path) + ': BEGIN'


def suite_end(file_path: pathlib.Path) -> str:
    return 'SUITE ' + str(file_path) + ': END'


def case(file_path: pathlib.Path, status: str) -> str:
    return 'CASE  ' + str(file_path) + ': ' + status


def summary_for_invalid_suite(file_path: pathlib.Path, exit_value: ExitValue) -> list:
    return ['',
            exit_value.exit_identifier]


def summary_for_valid_suite(file_path: pathlib.Path,
                            num_cases: int,
                            exit_value: ExitValue) -> list:
    num_tests_line = 'Ran 1 test' if num_cases == 1 else 'Ran %d tests' % num_cases
    return ['',
            num_tests_line,
            '',
            exit_value.exit_identifier]
