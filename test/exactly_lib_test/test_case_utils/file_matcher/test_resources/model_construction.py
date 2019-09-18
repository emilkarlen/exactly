import pathlib
from typing import Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib_test.test_case_utils.err_msg.test_resources import described_path

ModelConstructor = Callable[[HomeAndSds], DescribedPathPrimitive]


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(tcds: HomeAndSds) -> DescribedPathPrimitive:
        return described_path.new_primitive(pathlib.Path(file_name))

    return ret_val
