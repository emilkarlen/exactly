__author__ = 'emil'

import pathlib


class Configuration(tuple):

    def __new__(cls,
                home_dir: pathlib.Path,
                test_root_dir: pathlib.Path):
        return tuple.__new__(cls, (home_dir, test_root_dir))

    @property
    def home_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def test_root_dir(self) -> pathlib.Path:
        return self[1]