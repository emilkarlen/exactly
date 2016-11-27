import pathlib
import re

from exactly_lib.common.exit_value import ExitValue


class ExpectedLine:
    def __init__(self, suite_file_dir_abs_path: pathlib.Path):
        self.suite_file_dir_abs_path = suite_file_dir_abs_path

    def suite_begin(self, file_path: pathlib.Path) -> str:
        return 'suite ' + self._sub_file_path(file_path) + ': begin'

    def suite_end(self, file_path: pathlib.Path) -> str:
        return 'suite ' + self._sub_file_path(file_path) + ': end'

    def case(self, file_path: pathlib.Path, status: str) -> str:
        return 'case  ' + self._sub_file_path(file_path) + (': %s %s' % (TIME_VALUE_REPLACEMENT, status))

    def summary_for_invalid_suite(self,
                                  file_path: pathlib.Path,
                                  exit_value: ExitValue) -> list:
        return [exit_value.exit_identifier]

    def summary_for_valid_suite(self,
                                file_path: pathlib.Path,
                                exit_value: ExitValue) -> list:
        return [exit_value.exit_identifier]

    def _sub_file_path(self, file_path_abs_path: pathlib.Path) -> str:
        try:
            return str(file_path_abs_path.relative_to(self.suite_file_dir_abs_path))
        except ValueError:
            return str(file_path_abs_path)


def _replace_seconds_with_const(string_with_seconds_in_decimal_notation: str) -> str:
    return _TIME_ATTRIBUTE_RE.sub(TIME_VALUE_REPLACEMENT, string_with_seconds_in_decimal_notation)


replace_variable_output_with_placeholders = _replace_seconds_with_const

_TIME_ATTRIBUTE_RE = re.compile(r'\([0-9]+(\.[0-9]+)?s\)')
TIME_VALUE_REPLACEMENT = '(__TIME__s)'
