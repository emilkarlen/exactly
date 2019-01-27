import pathlib
from typing import Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds

ModelConstructor = Callable[[HomeAndSds], pathlib.Path]


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(tcds: HomeAndSds) -> pathlib.Path:
        return pathlib.Path(file_name)

    return ret_val
