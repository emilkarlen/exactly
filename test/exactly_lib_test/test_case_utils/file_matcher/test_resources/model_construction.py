import pathlib
from typing import Callable, TypeVar

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib_test.type_system.data.test_resources import described_path

MODEL = TypeVar('MODEL')

ModelConstructor = Callable[[FullResolvingEnvironment], DescribedPath]


def constant_model(model: DescribedPath) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> DescribedPath:
        return model

    return ret_val


def constant_relative_file_name(file_name: str) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> DescribedPath:
        return described_path.new_primitive(pathlib.Path(file_name))

    return ret_val
