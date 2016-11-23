import pathlib

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite.reporting import RootSuiteReporterFactory


class TestSuiteExecutionSettings:
    def __init__(self,
                 reporter_factory: RootSuiteReporterFactory,
                 handling_setup: TestCaseHandlingSetup,
                 suite_root_file_path: pathlib.Path):
        self.__reporter_factory = reporter_factory
        self.__handling_setup = handling_setup
        self.__suite_root_file_path = suite_root_file_path

    @property
    def reporter_factory(self) -> RootSuiteReporterFactory:
        return self.__reporter_factory

    @property
    def handling_setup(self) -> TestCaseHandlingSetup:
        return self.__handling_setup

    @property
    def suite_root_file_path(self) -> pathlib.Path:
        return self.__suite_root_file_path
