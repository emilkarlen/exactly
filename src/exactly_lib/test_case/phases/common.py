import pathlib

from exactly_lib.section_document.model import Instruction
from exactly_lib.test_case import sandbox_directory_structure as _sds
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.util.process_execution.process_execution_settings import ProcessExecutionSettings


class HomeAndSds:
    def __init__(self,
                 home_path: pathlib.Path,
                 sds: _sds.SandboxDirectoryStructure):
        self._home_path = home_path
        self._sds = sds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._home_path

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self._sds


class InstructionEnvironmentForPreSdsStep:
    def __init__(self,
                 home_dir: pathlib.Path,
                 environ: dict,
                 timeout_in_seconds: int = None):
        self.__home_dir = home_dir
        self.__timeout_in_seconds = timeout_in_seconds
        self.__environ = environ

    @property
    def home_directory(self) -> pathlib.Path:
        return self.__home_dir

    @property
    def environ(self) -> dict:
        """
        The set of environment variables available to instructions.
        These may be both read and written by instructions.
        """
        return self.__environ

    @property
    def timeout_in_seconds(self) -> int:
        """
        :return: None if no timeout
        """
        return self.__timeout_in_seconds

    @property
    def process_execution_settings(self) -> ProcessExecutionSettings:
        return ProcessExecutionSettings(self.timeout_in_seconds, self.environ)


class PhaseLoggingPaths:
    """
    Generator of unique logging directories for instructions in a given phase.
    """
    line_number_format = '{:03d}'

    def __init__(self,
                 log_root_dir: pathlib.Path,
                 phase_identifier: str):
        self._phase_dir_path = _sds.log_phase_dir(log_root_dir, phase_identifier)
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


class InstructionEnvironmentForPostSdsStep(InstructionEnvironmentForPreSdsStep):
    def __init__(self,
                 home_dir: pathlib.Path,
                 environ: dict,
                 sds: _sds.SandboxDirectoryStructure,
                 phase_identifier: str,
                 timeout_in_seconds: int = None):
        super().__init__(home_dir, environ, timeout_in_seconds)
        self.__sds = sds
        self._phase_logging = PhaseLoggingPaths(sds.log_dir, phase_identifier)

    @property
    def sandbox_directory_structure(self) -> _sds.SandboxDirectoryStructure:
        return self.__sds

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self.__sds

    @property
    def home_and_sds(self) -> HomeAndSds:
        return HomeAndSds(self.home_directory,
                          self.sds)

    @property
    def phase_logging(self) -> PhaseLoggingPaths:
        return self._phase_logging


class TestCaseInstruction(Instruction):
    @property
    def phase(self) -> Phase:
        raise NotImplementedError()
