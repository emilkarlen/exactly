import pathlib

from exactly_lib.section_document.model import Instruction
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable


class InstructionEnvironmentForPreSdsStep:
    def __init__(self,
                 hds: HomeDirectoryStructure,
                 environ: dict,
                 timeout_in_seconds: int = None,
                 symbols: SymbolTable = None):
        self.__hds = hds
        self.__timeout_in_seconds = timeout_in_seconds
        self.__environ = environ
        self.__symbols = SymbolTable() if symbols is None else symbols

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self.__hds

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

    @property
    def symbols(self) -> SymbolTable:
        return self.__symbols

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPreSds:
        return PathResolvingEnvironmentPreSds(self.__hds, self.__symbols)


class PhaseLoggingPaths:
    """
    Generator of unique logging directories for instructions in a given phase.
    """
    line_number_format = '{:03d}'
    instruction_file_format = 'instr-{:03d}'

    def __init__(self,
                 log_root_dir: pathlib.Path,
                 phase_identifier: str):
        self._phase_dir_path = _sds.log_phase_dir(log_root_dir, phase_identifier)
        self._visited_line_numbers = []
        self._next_instruction_number = 1

    @property
    def dir_path(self) -> pathlib.Path:
        return self._phase_dir_path

    def unique_instruction_file(self) -> pathlib.Path:
        instruction_number = self._next_instruction_number
        self._next_instruction_number += 1
        base_name = self.instruction_file_format.format(instruction_number)
        return self.dir_path / base_name

    def unique_instruction_file_as_existing_dir(self) -> pathlib.Path:
        path = self.unique_instruction_file()
        path.mkdir(parents=True, exist_ok=False)
        return path

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


class InstructionSourceInfo(tuple):
    def __new__(cls,
                source_line_number: int,
                instruction_name: str):
        return tuple.__new__(cls, (source_line_number,
                                   instruction_name))

    @property
    def instruction_name(self) -> str:
        return self[1]

    @property
    def line_number(self) -> int:
        return self[0]


def instruction_log_dir(phase_logging_paths: PhaseLoggingPaths,
                        source_info: InstructionSourceInfo) -> pathlib.Path:
    return phase_logging_paths.for_line(source_info.line_number, source_info.instruction_name)


class InstructionEnvironmentForPostSdsStep(InstructionEnvironmentForPreSdsStep):
    def __init__(self,
                 hds: HomeDirectoryStructure,
                 environ: dict,
                 sds: _sds.SandboxDirectoryStructure,
                 phase_identifier: str,
                 timeout_in_seconds: int = None,
                 symbols: SymbolTable = None):
        super().__init__(hds, environ, timeout_in_seconds, symbols)
        self.__sds = sds
        self._phase_logging = PhaseLoggingPaths(sds.log_dir, phase_identifier)

    @property
    def sds(self) -> _sds.SandboxDirectoryStructure:
        return self.__sds

    @property
    def home_and_sds(self) -> HomeAndSds:
        return HomeAndSds(self.hds,
                          self.sds)

    @property
    def phase_logging(self) -> PhaseLoggingPaths:
        return self._phase_logging

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPostSds:
        return PathResolvingEnvironmentPostSds(self.__sds, self.symbols)

    @property
    def path_resolving_environment_pre_or_post_sds(self) -> PathResolvingEnvironmentPreOrPostSds:
        return PathResolvingEnvironmentPreOrPostSds(self.home_and_sds, self.symbols)


class TestCaseInstruction(Instruction):
    @property
    def phase(self) -> Phase:
        raise NotImplementedError()


class SymbolUser:
    """
    An object that may use symbols.
    
    Such an object must be able to tell which symbols are used and how they are used.
    """

    def symbol_usages(self) -> list:
        """
        Gives information about all symbols that this instruction uses.

        This list should be available right after construction (and thus should not need
        any phase step to have been executed). The return value must be constant, with regard
        to the execution of other methods on the object (object of a sub class of this class).

        A symbol definition should not report references that the definition uses -
        these references are derived automatically via the definition object.

        :return: [`SymbolUsage`]
        """
        return []


class TestCaseInstructionWithSymbols(TestCaseInstruction, SymbolUser):
    @property
    def phase(self) -> Phase:
        raise NotImplementedError()
