import pathlib

from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType


class HomeDirectoryStructure(tuple):
    def __new__(cls,
                case_dir: pathlib.Path,
                act_dir: pathlib.Path):
        return tuple.__new__(cls, (case_dir,
                                   act_dir,
                                   {
                                       RelHomeOptionType.REL_HOME_CASE: case_dir,
                                       RelHomeOptionType.REL_HOME_ACT: act_dir,
                                   }))

    @property
    def case_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def act_dir(self) -> pathlib.Path:
        return self[1]

    def get(self, d: RelHomeOptionType) -> pathlib.Path:
        return self[2][d]
