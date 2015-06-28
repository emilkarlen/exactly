import pathlib

from shellcheck_lib_test.util.file_structure import DirContents


class Setup:
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        raise NotImplementedError()

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def suite_begin(self, file_path: pathlib.Path) -> str:
        return 'SUITE ' + str(file_path) + ': BEGIN'

    def suite_end(self, file_path: pathlib.Path) -> str:
        return 'SUITE ' + str(file_path) + ': END'

    def case(self, file_path: pathlib.Path, status: str) -> str:
        return 'CASE  ' + str(file_path) + ': ' + status
