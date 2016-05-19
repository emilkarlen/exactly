import pathlib

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


class TestSuite:
    """
    A root-suite with a hierarchy of sub-suites.
    """

    def __init__(self,
                 source_file: pathlib.Path,
                 file_inclusions_leading_to_this_file: list,
                 test_case_handling_setup: TestCaseHandlingSetup,
                 sub_test_suites: list,
                 test_cases: list):
        self.__source_file = source_file
        self.__file_inclusions_leading_to_this_file = file_inclusions_leading_to_this_file
        self.__test_case_handling_setup = test_case_handling_setup
        self.__sub_test_suites = sub_test_suites
        self.__test_cases = test_cases

    @property
    def source_file(self) -> pathlib.Path:
        return self.__source_file

    @property
    def file_inclusions_leading_to_this_file(self) -> list:
        return self.__file_inclusions_leading_to_this_file

    @property
    def test_case_handling_setup(self) -> TestCaseHandlingSetup:
        return self.__test_case_handling_setup

    @property
    def sub_test_suites(self) -> list:
        """
        :return: [TestSuite]
        """
        return self.__sub_test_suites

    @property
    def test_cases(self) -> list:
        """
        :return: [TestCaseSetup]
        """
        return self.__test_cases
