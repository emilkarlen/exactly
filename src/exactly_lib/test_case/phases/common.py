import pathlib

from exactly_lib.execution import execution_directory_structure as eds_module
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure, log_phase_dir
from exactly_lib.section_document.model import Instruction


class HomeAndEds:
    def __init__(self,
                 home_path: pathlib.Path,
                 eds: eds_module.ExecutionDirectoryStructure):
        self._home_path = home_path
        self._eds = eds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._home_path

    @property
    def eds(self) -> eds_module.ExecutionDirectoryStructure:
        return self._eds


class GlobalEnvironmentForPreEdsStep:
    def __init__(self,
                 home_dir: pathlib.Path,
                 timeout_in_seconds: int = None):
        self.__home_dir = home_dir
        self.__timeout_in_seconds = timeout_in_seconds

    @property
    def home_directory(self) -> pathlib.Path:
        return self.__home_dir

    @property
    def timeout_in_seconds(self) -> int:
        """
        :return: None if no timeout
        """
        return self.__timeout_in_seconds


class PhaseLoggingPaths:
    line_number_format = '{:03d}'

    def __init__(self,
                 log_root_dir: pathlib.Path,
                 phase_identifier: str):
        self._phase_dir_path = log_phase_dir(log_root_dir, phase_identifier)
        self._visited_line_numbers = []

    @property
    def dir_path(self) -> pathlib.Path:
        return self._phase_dir_path

    def for_line(self,
                 line_number: int,
                 tail: str = '') -> pathlib.Path:
        return self._phase_dir_path / self.__line_suffix(line_number, tail)

    def __line_suffix(self, line_number, tail) -> str:
        num_previous_visited = self._visited_line_numbers.count(line_number)
        self._visited_line_numbers.append(line_number)
        if num_previous_visited == 0:
            head = self.line_number_format.format(line_number)
            if tail:
                return head + '--' + tail
            else:
                return head
        else:
            head = (self.line_number_format.format(line_number)) + ('-%d' % (num_previous_visited + 1))
            if tail:
                return head + '-' + tail
            else:
                return head


class GlobalEnvironmentForPostEdsPhase(GlobalEnvironmentForPreEdsStep):
    def __init__(self,
                 home_dir: pathlib.Path,
                 eds: ExecutionDirectoryStructure,
                 phase_identifier: str):
        super().__init__(home_dir)
        self.__eds = eds
        self._phase_logging = PhaseLoggingPaths(eds.log_dir, phase_identifier)

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self.__eds

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self.__eds

    @property
    def home_and_eds(self) -> HomeAndEds:
        return HomeAndEds(self.home_directory,
                          self.eds)

    @property
    def phase_logging(self) -> PhaseLoggingPaths:
        return self._phase_logging


class TestCaseInstruction(Instruction):
    pass
