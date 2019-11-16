import pathlib
from typing import Callable

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib_test.type_system.data.test_resources import described_path

ModelConstructor = Callable[[Tcds], DescribedPathPrimitive]


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(tcds: Tcds) -> DescribedPathPrimitive:
        return described_path.new_primitive(pathlib.Path(file_name))

    return ret_val
