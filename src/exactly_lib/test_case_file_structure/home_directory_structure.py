import pathlib

from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType


class HomeDirectoryStructure(tuple):
    def __new__(cls,
                case_dir: pathlib.Path,
                act_dir: pathlib.Path):
        return tuple.__new__(cls, (case_dir,
                                   act_dir,
                                   {
                                       RelHdsOptionType.REL_HDS_CASE: case_dir,
                                       RelHdsOptionType.REL_HDS_ACT: act_dir,
                                   }))

    @property
    def case_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def act_dir(self) -> pathlib.Path:
        return self[1]

    def get(self, d: RelHdsOptionType) -> pathlib.Path:
        return self[2][d]
