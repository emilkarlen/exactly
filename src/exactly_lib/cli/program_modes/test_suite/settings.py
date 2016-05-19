import pathlib

from exactly_lib.cli.test_case_handling_setup import TestCaseHandlingSetup


class TestSuiteExecutionSettings:
    def __init__(self,
                 handling_setup: TestCaseHandlingSetup,
                 suite_root_file_path: pathlib.Path):
        self.__handling_setup = handling_setup
        self.__suite_root_file_path = suite_root_file_path

    @property
    def handling_setup(self) -> TestCaseHandlingSetup:
        return self.__handling_setup

    @property
    def suite_root_file_path(self) -> pathlib.Path:
        return self.__suite_root_file_path
