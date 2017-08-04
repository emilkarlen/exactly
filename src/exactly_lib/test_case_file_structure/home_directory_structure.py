import pathlib


class HomeDirectoryStructure:
    def __init__(self,
                 case_home: pathlib.Path):
        self._case_home = case_home

    @property
    def case_dir(self) -> pathlib.Path:
        return self._case_home
