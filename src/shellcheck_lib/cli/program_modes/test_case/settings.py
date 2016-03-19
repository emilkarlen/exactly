import enum
import pathlib

from shellcheck_lib.test_case.phases.act.phase_setup import ActPhaseSetup
from shellcheck_lib.test_case.test_case_processing import Preprocessor


class Output(enum.Enum):
    STATUS_CODE = 1
    EXECUTION_DIRECTORY_STRUCTURE_ROOT = 2
    ACT_PHASE_OUTPUT = 3


class TestCaseExecutionSettings:
    def __init__(self,
                 file_path: pathlib.Path,
                 initial_home_dir_path: pathlib.Path,
                 output: Output,
                 preprocessor: Preprocessor,
                 act_phase_setup: ActPhaseSetup,
                 is_keep_execution_directory_root: bool=False,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self.__file_path = file_path
        self.__initial_home_dir_path = initial_home_dir_path
        self.__output = output
        self.__preprocessor = preprocessor
        self.__is_keep_execution_directory_root = is_keep_execution_directory_root
        self.__execution_directory_root_name_prefix = execution_directory_root_name_prefix
        self.__act_phase_setup = act_phase_setup

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
    def preprocessor(self) -> Preprocessor:
        return self.__preprocessor

    @property
    def is_keep_execution_directory_root(self) -> bool:
        return self.__is_keep_execution_directory_root

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self.__execution_directory_root_name_prefix

    @property
    def act_phase_setup(self) -> ActPhaseSetup:
        return self.__act_phase_setup
