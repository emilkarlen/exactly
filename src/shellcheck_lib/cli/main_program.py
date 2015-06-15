import enum
import pathlib


class Output(enum.Enum):
    STATUS_CODE = 1
    EXECUTION_DIRECTORY_STRUCTURE_ROOT = 2
    ACT_PHASE_OUTPUT = 3


class TestCaseExecutionSettings:
    def __init__(self,
                 file_path: pathlib.Path,
                 initial_home_dir_path: pathlib.Path,
                 output: Output,
                 is_keep_execution_directory_root: bool=False,
                 execution_directory_root_name_prefix: str='shellcheck-',
                 interpreter: str=None):
        self.__file_path = file_path
        self.__initial_home_dir_path = initial_home_dir_path
        self.__output = output
        self.__is_keep_execution_directory_root = is_keep_execution_directory_root
        self.__execution_directory_root_name_prefix = execution_directory_root_name_prefix
        self.__interpreter = interpreter

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
    def is_keep_execution_directory_root(self) -> bool:
        return self.__is_keep_execution_directory_root

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self.__execution_directory_root_name_prefix

    @property
    def interpreter(self) -> str:
        return self.__interpreter


class MainProgram:
    def execute(self,
                command_line_arguments: list):
        raise NotImplementedError()

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings):
        raise NotImplementedError()
