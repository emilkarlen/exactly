import pathlib

from shellcheck_lib.test_suite import reporting
from shellcheck_lib.test_suite.structure import SuiteEnumerator

EXIT__INVALID_SUITE_STRUCTURE = 3


class TestSuiteExecutionSettings:
    def __init__(self,
                 reporter_factory: reporting.ReporterFactory,
                 suite_enumerator: SuiteEnumerator,
                 suite_root_file_path: pathlib.Path):
        self.__reporter_factory = reporter_factory
        self.__suite_enumerator = suite_enumerator
        self.__suite_root_file_path = suite_root_file_path

    @property
    def reporter_factory(self) -> reporting.ReporterFactory:
        return self.__reporter_factory

    @property
    def suite_enumerator(self) -> SuiteEnumerator:
        return self.__suite_enumerator

    @property
    def suite_root_file_path(self) -> pathlib.Path:
        return self.__suite_root_file_path

