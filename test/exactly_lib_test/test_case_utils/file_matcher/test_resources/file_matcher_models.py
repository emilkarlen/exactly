import pathlib

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib_test.type_system.data.test_resources import described_path


def new_model(path: pathlib.Path) -> FileMatcherModel:
    return FileMatcherModelForPrimitivePath(described_path.new_primitive(path))


def new_model__of_described(path: DescribedPathPrimitive) -> FileMatcherModel:
    return FileMatcherModelForPrimitivePath(path)
