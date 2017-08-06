import pathlib


class HomeDirectoryStructure:
    def __init__(self,
                 case_dir: pathlib.Path,
                 act_dir: pathlib.Path):
        self._case_dir = case_dir
        self._act_dir = act_dir

    @property
    def case_dir(self) -> pathlib.Path:
        return self._case_dir

    @property
    def act_dir(self) -> pathlib.Path:
        return self._act_dir
