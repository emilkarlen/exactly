import pathlib
from typing import Callable, TypeVar

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib_test.type_system.data.test_resources import described_path

MODEL = TypeVar('MODEL')

ModelConstructor = Callable[[FullResolvingEnvironment], DescribedPathPrimitive]


def constant_model(model: DescribedPathPrimitive) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> DescribedPathPrimitive:
        return model

    return ret_val


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> DescribedPathPrimitive:
        return described_path.new_primitive(pathlib.Path(file_name))

    return ret_val
