import pathlib
from pathlib import Path
from typing import List

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import TestCaseFileReference


class TestSuiteHierarchy:
    """
    A root-suite with a hierarchy of sub-suites.
    """

    def __init__(self,
                 source_file: pathlib.Path,
                 suite_file_inclusions_leading_to_this_file: List[Path],
                 test_case_handling_setup: TestCaseHandlingSetup,
                 sub_test_suites: List['TestSuiteHierarchy'],
                 test_cases: List[TestCaseFileReference]):
        self.__source_file = source_file
        self.__suite_file_inclusions_leading_to_this_file = suite_file_inclusions_leading_to_this_file
        self.__test_case_handling_setup = test_case_handling_setup
        self.__sub_test_suites = sub_test_suites
        self.__test_cases = test_cases

    @property
    def source_file(self) -> pathlib.Path:
        return self.__source_file

    @property
    def suite_file_inclusions_leading_to_this_file(self) -> List[Path]:
        return self.__suite_file_inclusions_leading_to_this_file

    @property
    def test_case_handling_setup(self) -> TestCaseHandlingSetup:
        return self.__test_case_handling_setup

    @property
    def sub_test_suites(self) -> List['TestSuiteHierarchy']:
        return self.__sub_test_suites

    @property
    def test_cases(self) -> List[TestCaseFileReference]:
        return self.__test_cases
