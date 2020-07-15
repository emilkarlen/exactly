import pathlib

from exactly_lib.common import tmp_file_spaces
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.util.file_utils.tmp_file_space import TmpFileSpace, TmpDirFileSpace


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


class PhaseLoggingPaths(TmpFileSpace):
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

    def new_path(self) -> pathlib.Path:
        return self.unique_instruction_file()

    def unique_instruction_file(self) -> pathlib.Path:
        instruction_number = self._next_instruction_number
        self._next_instruction_number += 1
        base_name = self.instruction_file_format.format(instruction_number)
        return self.dir_path / base_name

    def unique_instruction_file_as_existing_dir(self) -> pathlib.Path:
        return self.new_path_as_existing_dir()

    def space_for_instruction(self) -> TmpDirFileSpace:
        return tmp_file_spaces.std_tmp_dir_file_space(
            self.unique_instruction_file(),
        )

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


def instruction_log_dir(phase_logging_paths: PhaseLoggingPaths,
                        source_info: InstructionSourceInfo) -> pathlib.Path:
    return phase_logging_paths.for_line(source_info.line_number, source_info.instruction_name)
