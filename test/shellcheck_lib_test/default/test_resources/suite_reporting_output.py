import pathlib

from shellcheck_lib.cli.cli_environment.exit_value import ExitValue


class ExpectedLine:
    def __init__(self, suite_file_abs_path: pathlib.Path):
        self.suite_file_abs_path = suite_file_abs_path

    def suite_begin(self, file_path: pathlib.Path) -> str:
        return 'suite ' + self._sub_file_path(file_path) + ': begin'

    def suite_end(self, file_path: pathlib.Path) -> str:
        return 'suite ' + self._sub_file_path(file_path) + ': end'

    def case(self, file_path: pathlib.Path, status: str) -> str:
        return 'case  ' + self._sub_file_path(file_path) + ': ' + status

    def summary_for_invalid_suite(self,
                                  file_path: pathlib.Path,
                                  exit_value: ExitValue) -> list:
        return [exit_value.exit_identifier]

    def summary_for_valid_suite(self,
                                file_path: pathlib.Path,
                                exit_value: ExitValue) -> list:
        return [exit_value.exit_identifier]

    def _sub_file_path(self, file_path_abs_path: pathlib.Path):
        return str(file_path_abs_path)
