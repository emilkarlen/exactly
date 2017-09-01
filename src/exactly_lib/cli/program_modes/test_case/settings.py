import enum
import pathlib

from exactly_lib import program_info
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


class ReportingOption(enum.Enum):
    STATUS_CODE = 1
    SANDBOX_DIRECTORY_STRUCTURE_ROOT = 2
    ACT_PHASE_OUTPUT = 3


class TestCaseExecutionSettings:
    """Settings derived after parsing of command line arguments."""

    def __init__(self,
                 test_case_file_path: pathlib.Path,
                 initial_home_dir_path: pathlib.Path,
                 output: ReportingOption,
                 handling_setup: TestCaseHandlingSetup,
                 sandbox_directory_root_name_prefix: str = program_info.PROGRAM_NAME + '-',
                 suite_to_read_config_from: pathlib.Path = None,
                 ):
        self.__test_case_file_path = test_case_file_path
        self.__initial_home_dir_path = initial_home_dir_path
        self.__output = output
        self.__handling_setup = handling_setup
        self.__sandbox_directory_root_name_prefix = sandbox_directory_root_name_prefix
        self.__suite_to_read_config_from = suite_to_read_config_from

    @property
    def test_case_file_path(self) -> pathlib.Path:
        return self.__test_case_file_path

    @property
    def initial_home_dir_path(self) -> pathlib.Path:
        return self.__initial_home_dir_path

    @property
    def reporting_option(self) -> ReportingOption:
        return self.__output

    @property
    def handling_setup(self) -> TestCaseHandlingSetup:
        return self.__handling_setup

    @property
    def sandbox_directory_root_name_prefix(self) -> str:
        return self.__sandbox_directory_root_name_prefix

    @property
    def suite_to_read_config_from(self) -> pathlib.Path:
        """
        If this is not None, then a suite file has been given,
        and config should be read from that file and
        used as default.
        :return: None iff config should not be read from a suite.
        """
        return self.__suite_to_read_config_from
