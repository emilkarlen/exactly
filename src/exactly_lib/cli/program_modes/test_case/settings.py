import enum
import pathlib

from exactly_lib import program_info
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


class Output(enum.Enum):
    STATUS_CODE = 1
    EXECUTION_DIRECTORY_STRUCTURE_ROOT = 2
    ACT_PHASE_OUTPUT = 3


class TestCaseExecutionSettings:
    def __init__(self,
                 file_path: pathlib.Path,
                 initial_home_dir_path: pathlib.Path,
                 output: Output,
                 handling_setup: TestCaseHandlingSetup,
                 is_keep_execution_directory_root: bool=False,
                 execution_directory_root_name_prefix: str= program_info.PROGRAM_NAME + '-'):
        self.__file_path = file_path
        self.__initial_home_dir_path = initial_home_dir_path
        self.__output = output
        self.__handling_setup = handling_setup
        self.__is_keep_execution_directory_root = is_keep_execution_directory_root
        self.__execution_directory_root_name_prefix = execution_directory_root_name_prefix

    @property
    def file_path(self) -> pathlib.Path:
        return self.__file_path

    @property
    def initial_home_dir_path(self) -> pathlib.Path:
        return self.__initial_home_dir_path

    @property
    def output(self) -> Output:
        return self.__output

    @property
    def handling_setup(self) -> TestCaseHandlingSetup:
        return self.__handling_setup

    @property
    def is_keep_execution_directory_root(self) -> bool:
        return self.__is_keep_execution_directory_root

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self.__execution_directory_root_name_prefix
