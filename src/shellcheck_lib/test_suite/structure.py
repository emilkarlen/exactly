import pathlib


class TestCase:
    def __init__(self,
                 file_path: pathlib.Path):
        self.__file_path = file_path

    @property
    def file_path(self) -> pathlib.Path:
        return self.__file_path


class TestSuite:
    """
    A root-suite with a hierarchy of sub-suites.
    """

    def __init__(self,
                 source_file: pathlib.Path,
                 file_inclusions_leading_to_this_file: list,
                 sub_test_suites: list,
                 test_cases: list):
        self.__source_file = source_file
        self.__file_inclusions_leading_to_this_file = file_inclusions_leading_to_this_file
        self.__sub_test_suites = sub_test_suites
        self.__test_cases = test_cases

    @property
    def source_file(self) -> pathlib.Path:
        return self.__source_file

    @property
    def file_inclusions_leading_to_this_file(self) -> list:
        return self.__file_inclusions_leading_to_this_file

    @property
    def sub_test_suites(self) -> list:
        """
        :return: [TestSuite]
        """
        return self.__sub_test_suites

    @property
    def test_cases(self) -> list:
        """
        :return: [TestCase]
        """
        return self.__test_cases
