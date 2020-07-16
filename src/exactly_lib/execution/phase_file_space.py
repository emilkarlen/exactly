import pathlib

from exactly_lib.common import tmp_dir_file_spaces
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.instruction_environment import TmpFileStorage
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class PhaseTmpFileSpaceFactory:
    VALIDATION_SUB_DIR = 'validation'

    def __init__(self, root_dir: pathlib.Path):
        self._root_dir = root_dir

    def for_phase__validation(self,
                              phase: phase_identifier.Phase,
                              ) -> TmpFileStorage:
        return TmpFileStorage(
            self._root_dir / _phase_dir(phase) / PhaseTmpFileSpaceFactory.VALIDATION_SUB_DIR,
            _get_paths_access_for_dir
        )

    def for_phase__main(self,
                        phase: phase_identifier.Phase,
                        ) -> TmpFileStorage:
        return TmpFileStorage(
            self._root_dir / _phase_dir(phase),
            _get_paths_access_for_dir
        )

    def instruction__validation(self,
                                phase: phase_identifier.Phase,
                                instruction_number: int,
                                ) -> TmpFileStorage:
        root_dir = self._root_dir / self.VALIDATION_SUB_DIR
        return TmpFileStorage(
            root_dir / _instruction_sub_dir(phase, instruction_number),
            _get_paths_access_for_dir
        )

    def instruction__main(self,
                          phase: phase_identifier.Phase,
                          instruction_number: int,
                          ) -> TmpFileStorage:
        return TmpFileStorage(
            self._root_dir / _instruction_sub_dir(phase, instruction_number),
            _get_paths_access_for_dir
        )


def _instruction_sub_dir(phase: phase_identifier.Phase,
                         instruction_number: int,
                         ) -> pathlib.Path:
    phase_dir = '-'.join((
        str(phase.the_enum.value),
        phase.identifier,
    ))
    instr_dir = str(instruction_number).zfill(3)

    return pathlib.Path(phase_dir) / instr_dir


def _phase_dir(phase: phase_identifier.Phase) -> str:
    return '-'.join((
        str(phase.the_enum.value),
        phase.identifier,
    ))


def _get_paths_access_for_dir(root_dir: pathlib.Path) -> DirFileSpace:
    return tmp_dir_file_spaces.std_tmp_dir_file_space(root_dir)
