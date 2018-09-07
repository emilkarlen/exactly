import pathlib

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite.reporting import RootSuiteProcessingReporter


class TestSuiteExecutionSettings:
    def __init__(self,
                 reporter: RootSuiteProcessingReporter,
                 handling_setup: TestCaseHandlingSetup,
                 suite_root_file_path: pathlib.Path):
        self.__reporter = reporter
        self.__handling_setup = handling_setup
        self.__suite_root_file_path = suite_root_file_path

    @property
    def processing_reporter(self) -> RootSuiteProcessingReporter:
        return self.__reporter

    @property
    def handling_setup(self) -> TestCaseHandlingSetup:
        return self.__handling_setup

    @property
    def suite_root_file_path(self) -> pathlib.Path:
        return self.__suite_root_file_path
