import pathlib

from exactly_lib.impls.types.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path


def new_model(path: pathlib.Path) -> FileMatcherModel:
    return FileMatcherModelForDescribedPath(described_path.new_primitive(path))


def new_model__of_described(path: DescribedPath) -> FileMatcherModel:
    return FileMatcherModelForDescribedPath(path)
