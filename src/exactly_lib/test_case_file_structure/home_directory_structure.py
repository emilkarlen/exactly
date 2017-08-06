import pathlib


class HomeDirectoryStructure(tuple):
    def __new__(cls,
                case_dir: pathlib.Path,
                act_dir: pathlib.Path):
        return tuple.__new__(cls, (case_dir,
                                   act_dir))

    @property
    def case_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def act_dir(self) -> pathlib.Path:
        return self[1]
