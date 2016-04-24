import pathlib
import re

from shellcheck_lib.cli.cli_environment.exit_value import ExitValue


def suite_begin(file_path: pathlib.Path) -> str:
    return 'suite ' + str(file_path) + ': begin'


def suite_end(file_path: pathlib.Path) -> str:
    return 'suite ' + str(file_path) + ': end'


def case(file_path: pathlib.Path, status: str) -> str:
        return 'case  ' + str(file_path) + ': ' + status


def summary_for_invalid_suite(file_path: pathlib.Path, exit_value: ExitValue) -> list:
    return ['',
            exit_value.exit_identifier]


def summary_for_valid_suite(file_path: pathlib.Path,
                            num_cases: int,
                            exit_value: ExitValue,
                            errors=frozenset()) -> list:
    """
    :type errors: dict ExitValue -> int
    """
    lines = []
    lines.extend(['', _num_tests_and_timing_line(num_cases)])
    if errors:
        lines.extend(_error_lines(errors))
    lines.extend(['', exit_value.exit_identifier])
    return lines


def _error_lines(errors: dict):
    ret_val = ['']
    sorted_exit_values = sorted(errors.keys(), key=ExitValue.exit_identifier.fget)
    max_identifier_len = max([len(exit_value.exit_identifier) for exit_value in sorted_exit_values])
    format_str = '%-' + str(max_identifier_len) + 's : %d'
    for exit_value in sorted_exit_values:
        ret_val.append(format_str % (exit_value.exit_identifier, errors[exit_value]))
    return ret_val


def _num_tests_and_timing_line(num_cases):
    parts = ['Ran']
    num_tests_prefix = '1 test' if num_cases == 1 else '%d tests' % num_cases
    parts.append(num_tests_prefix)
    parts.append('in')
    parts.append('.*')
    num_tests_line_re = re.compile(' '.join(parts))
    return num_tests_line_re
